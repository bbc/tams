import os
from functools import wraps
from uuid import UUID

from token_checker import verify_token, get_signing_key, get_groups_in_token
from resources import Tams
from permissions import any_is_admin, filter_read
from httpx import AsyncClient
from sanic import Sanic
from sanic.log import logger
from sanic.request import Request
from sanic.exceptions import Forbidden, InvalidUsage, NotFound

app = Sanic("ProxyApp")
app.config.CORS_ORIGINS = "*"


@app.before_server_start
async def setup_client(app):
    client = AsyncClient()
    app.ctx.api_url = os.environ["API_URL"]
    app.ctx.jwks_client = get_signing_key(os.environ.get("JWKS_URL"))
    app.ctx.tams = Tams(client, logger, app.ctx.api_url)


def handle_token():
    """Decorator that verifies token in request, and extracts the embedded groups"""
    def decorator(f):
        @wraps(f)
        async def decorated_function(request: Request, *args, **kwargs):
            del (request.headers["host"])

            token = verify_token(request, app.ctx.jwks_client)
            groups = get_groups_in_token(token)

            return await f(request, groups, *args, **kwargs)
        return decorated_function
    return decorator


def passthrough_if_admin():
    """Decorator that passes through the request if the user is an admin"""
    def decorator(f):
        @wraps(f)
        async def decorated_function(request: Request, groups: list[str], *args, **kwargs):
            # Passthrough request if request has admin permissions
            if any_is_admin(groups):
                return await app.ctx.tams.passthrough_request(request)

            # Otherwise process based on decorated function
            return await f(request, groups, *args, **kwargs)
        return decorated_function
    return decorator


@app.route('/<path:path>', methods=["OPTIONS"])
async def options_all(request: Request, path: str):
    del (request.headers["host"])
    return await app.ctx.tams.passthrough_request(request)


@app.route('/', methods=['GET', 'HEAD'])
@handle_token()
async def root(request: Request, groups: list[str]):
    # Available to all
    return await app.ctx.tams.passthrough_request(request)


@app.route('/service', methods=['GET', 'HEAD'])
@handle_token()
async def service(request: Request, groups: list[str]):
    # Available to all
    return await app.ctx.tams.passthrough_request(request)


@app.route('/service', methods=['POST'])
@handle_token()
@passthrough_if_admin()
async def post_service(request: Request, groups: list[str]):
    # Admin only (bypassed by `passthrough_if_admin` decorator above)
    raise Forbidden("Insufficient permissions")


@app.route('/service/storage-backends', methods=['GET', 'HEAD'])
@handle_token()
async def storage_backends(request: Request, groups: list[str]):
    # Available to all
    return await app.ctx.tams.passthrough_request(request)


@app.route('/service/webhooks', methods=['GET', 'HEAD'])
@handle_token()
@passthrough_if_admin()
async def webhooks(request: Request, groups: list[str]):
    # Restrict returned data to only the webhooks that the request has read permission on.
    filtered_groups = filter_read(groups)
    return await app.ctx.tams.filtered_webhooks(request, filtered_groups)


@app.route('/service/webhooks', methods=['POST'])
@handle_token()
@passthrough_if_admin()
async def post_webhooks(request: Request, groups: list[str]):
    # If the request includes Source or Flow filters,
    # the request must have read permissions on all Source or Flow IDs requested.
    # Otherwise, reject.
    # Note that this endpoint only allows creation, not modification, of webhooks.
    #
    # NOTE: This implementation will only accept requests where IDs are provided.
    # Where collected by IDs are provided, they are evaluated on webhook generation only
    # Wildcard webhooks may be created by an admin, in which case the request is passed through.

    # Verify and flatten webhook Source/Flow IDs based on permissions
    await app.ctx.tams.validate_webhook(request, groups)
    static_request = await app.ctx.tams.static_webhook(request, groups)
    return await app.ctx.tams.passthrough_request(static_request)


@app.route('/service/webhooks/<webhook_id:uuid>', methods=['GET', 'HEAD'])
@handle_token()
@passthrough_if_admin()
async def webhook(request: Request, groups: list[str], webhook_id: UUID):
    # Request must have read permissions on {webhookId}.
    (await app.ctx.tams.Webhook(request, webhook_id)).has_read(groups, throw=True)
    return await app.ctx.tams.passthrough_request(request)


@app.route('/service/webhooks/<webhook_id:uuid>', methods=['PUT'])
@handle_token()
@passthrough_if_admin()
async def put_webhook(request: Request, groups: list[str], webhook_id: UUID):
    # Request must have write permissions on {webhookId}.
    # If the request includes Source or Flow filters,
    # the request must have read permissions on all Source or Flow IDs requested.
    #
    # NOTE: This implementation will only accept requests where IDs are provided.
    # Where collected by IDs are provided, they are evaluated on webhook generation only
    # Wildcard webhooks may be created by an admin, in which case the request is passed through.
    webhook = await app.ctx.tams.Webhook(request, webhook_id)
    webhook.has_write(groups, throw=True)

    new_auth_classes = request.json.get("tags", {}).get("auth_classes", [])
    webhook.validate_modify_auth_classes(new_auth_classes, groups)

    # Verify and flatten webhook Source/Flow IDs based on permissions
    await app.ctx.tams.validate_webhook(request, groups)
    static_request = await app.ctx.tams.static_webhook(request, groups)

    return await app.ctx.tams.passthrough_request(static_request)


@app.route('/service/webhooks/<webhook_id:uuid>', methods=['DELETE'])
@handle_token()
@passthrough_if_admin()
async def delete_webhook(request: Request, groups: list[str], webhook_id: UUID):
    (await app.ctx.tams.Webhook(request, webhook_id)).has_delete(groups, throw=True)
    return await app.ctx.tams.passthrough_request(request)


@app.route('/sources', methods=['GET', 'HEAD'])
@handle_token()
@passthrough_if_admin()
async def sources(request: Request, groups: list[str]):
    # Restrict the returned data to only the Sources that the request has read permission on.
    filtered_groups = filter_read(groups)
    return await app.ctx.tams.filtered_sources(request, filtered_groups)


@app.route('/sources/<source_id:uuid>', methods=['GET', 'HEAD'])
@handle_token()
@passthrough_if_admin()
async def source(request: Request, groups: list[str], source_id: UUID):
    # Request must have read permissions on {sourceId}.
    (await app.ctx.tams.Source(request, source_id)).has_read(groups, throw=True)
    return await app.ctx.tams.passthrough_request(request)


@app.route('/sources/<source_id:uuid>/tags', methods=['GET', 'HEAD'])
@handle_token()
@passthrough_if_admin()
async def source_tags(request: Request, groups: list[str], source_id: UUID):
    # Request must have read permissions on {sourceId}.
    (await app.ctx.tams.Source(request, source_id)).has_read(groups, throw=True)
    return await app.ctx.tams.passthrough_request(request)


@app.route('/sources/<source_id:uuid>/tags/<tag_name>', methods=['GET', 'HEAD'])
@handle_token()
@passthrough_if_admin()
async def source_tag(request: Request, groups: list[str], source_id: UUID, tag_name: str):
    # Request must have read permissions on {sourceId}.
    (await app.ctx.tams.Source(request, source_id)).has_read(groups, throw=True)
    return await app.ctx.tams.passthrough_request(request)


@app.route('/sources/<source_id:uuid>/tags/<tag_name>', methods=['PUT'])
@handle_token()
@passthrough_if_admin()
async def put_source_tag(request: Request, groups: list[str], source_id: UUID, tag_name: str):
    # Request must have write permissions on {sourceId}.
    # Must not permit addition of permissions the request doesn't claim.
    source = await app.ctx.tams.Source(request, source_id)
    source.has_write(groups, throw=True)

    if tag_name == "auth_classes":
        new_auth_classes = request.json
        source.validate_modify_auth_classes(new_auth_classes, groups)
    return await app.ctx.tams.passthrough_request(request)


@app.route('/sources/<source_id:uuid>/tags/<tag_name>', methods=['DELETE'])
@handle_token()
@passthrough_if_admin()
async def delete_source_tag(request: Request, groups: list[str], source_id: UUID, tag_name: str):
    # Request must have write permissions on {sourceId}.
    source = await app.ctx.tams.Source(request, source_id)
    source.has_write(groups, throw=True)

    if tag_name == "auth_classes":
        # Check has permissions that will be removed
        source.validate_modify_auth_classes([], groups)

    return await app.ctx.tams.passthrough_request(request)


@app.route('/sources/<source_id:uuid>/description', methods=['GET', 'HEAD'])
@handle_token()
@passthrough_if_admin()
async def source_description(request: Request, groups: list[str], source_id: UUID):
    # Request must have read permissions on {sourceId}.
    (await app.ctx.tams.Source(request, source_id)).has_read(groups, throw=True)
    return await app.ctx.tams.passthrough_request(request)


@app.route('/sources/<source_id:uuid>/description', methods=['PUT', 'DELETE'])
@handle_token()
@passthrough_if_admin()
async def put_del_source_description(request: Request, groups: list[str], source_id: UUID):
    # Request must have write permissions on {sourceId}.
    (await app.ctx.tams.Source(request, source_id)).has_write(groups, throw=True)
    return await app.ctx.tams.passthrough_request(request)


@app.route('/sources/<source_id:uuid>/label', methods=['GET', 'HEAD'])
@handle_token()
@passthrough_if_admin()
async def source_label(request: Request, groups: list[str], source_id: UUID):
    # Request must have read permissions on {sourceId}.
    (await app.ctx.tams.Source(request, source_id)).has_read(groups, throw=True)
    return await app.ctx.tams.passthrough_request(request)


@app.route('/sources/<source_id:uuid>/label', methods=['PUT', 'DELETE'])
@handle_token()
@passthrough_if_admin()
async def put_del_source_label(request: Request, groups: list[str], source_id: UUID):
    # Request must have write permissions on {sourceId}.
    (await app.ctx.tams.Source(request, source_id)).has_write(groups, throw=True)
    return await app.ctx.tams.passthrough_request(request)


@app.route('/flows', methods=['GET', 'HEAD'])
@handle_token()
@passthrough_if_admin()
async def flows(request: Request, groups: list[str]):
    # Restrict returned data to only the Flows that the request has read permission on.
    filtered_groups = filter_read(groups)
    return await app.ctx.tams.filtered_flows(request, filtered_groups)


@app.route('/flows/<flow_id:uuid>', methods=['GET', 'HEAD'])
@handle_token()
@passthrough_if_admin()
async def flow(request: Request, groups: list[str], flow_id: UUID):
    # Request must have read permissions on {flowID}.
    (await app.ctx.tams.Flow(request, flow_id)).has_read(groups, throw=True)
    return await app.ctx.tams.passthrough_request(request)


@app.route('/flows/<flow_id:uuid>', methods=['PUT'])
@handle_token()
@passthrough_if_admin()
async def put_flow(request: Request, groups: list[str], flow_id: UUID):
    # If {flowId} does not currently exist, request must have write permissions on the Flow's Source ID
    # if it already exists in this TAMS instance.
    # If neither {flowId} nor the Source ID exist, allow if the request has create permission
    # (see Creating new Flows and Sources).
    # If {flowId} already exists, request must have write permissions on {flowId}.

    # Note: It is assumed that the "create permission" restriction mentioned above
    # is implemented in the upstream API
    flow = await app.ctx.tams.Flow(request, flow_id)
    if flow.exists:
        # Update Flow
        flow.has_write(groups, throw=True)

        new_auth_classes = request.json.get("tags", {}).get("auth_classes", [])
        flow.validate_modify_auth_classes(new_auth_classes, groups)
    else:
        # Create flow
        source_id = request.json.get("source_id", None)
        if not source_id:
            raise InvalidUsage("Missing source_id")
        else:
            source = await app.ctx.tams.Source(request, source_id)
            if source.exists:
                # If the Source exists, verify the request has write access on it
                source.has_write(groups, throw=True)

    return await app.ctx.tams.passthrough_request(request)


@app.route('/flows/<flow_id:uuid>', methods=['DELETE'])
@handle_token()
@passthrough_if_admin()
async def delete_flow(request: Request, groups: list[str], flow_id: UUID):
    # Request must have delete permissions on {flowId}.
    (await app.ctx.tams.Flow(request, flow_id)).has_delete(groups, throw=True)
    return await app.ctx.tams.passthrough_request(request)


@app.route('/flows/<flow_id:uuid>/tags', methods=['GET', 'HEAD'])
@handle_token()
@passthrough_if_admin()
async def flow_tags(request: Request, groups: list[str], flow_id: UUID):
    # Request must have read permissions on {flowID}.
    (await app.ctx.tams.Flow(request, flow_id)).has_read(groups, throw=True)
    return await app.ctx.tams.passthrough_request(request)


@app.route('/flows/<flow_id:uuid>/tags/<tag_name>', methods=['GET', 'HEAD'])
@handle_token()
@passthrough_if_admin()
async def flow_tag(request: Request, groups: list[str], flow_id: UUID, tag_name: str):
    # Request must have read permissions on {flowID}.
    (await app.ctx.tams.Flow(request, flow_id)).has_read(groups, throw=True)
    return await app.ctx.tams.passthrough_request(request)


@app.route('/flows/<flow_id:uuid>/tags/<tag_name>', methods=['PUT'])
@handle_token()
@passthrough_if_admin()
async def put_flow_tag(request: Request, groups: list[str], flow_id: UUID, tag_name: str):
    # Request must have write permissions on {flowId}.
    # Must not permit addition of permissions the request doesn't claim.
    flow = await app.ctx.tams.Flow(request, flow_id)
    flow.has_write(groups, throw=True)

    if tag_name == "auth_classes":
        new_auth_classes = request.json
        flow.validate_modify_auth_classes(new_auth_classes, groups)

    return await app.ctx.tams.passthrough_request(request)


@app.route('/flows/<flow_id:uuid>/tags/<tag_name>', methods=['DELETE'])
@handle_token()
@passthrough_if_admin()
async def delete_flow_tag(request: Request, groups: list[str], flow_id: UUID, tag_name: str):
    # Request must have write permissions on {flowId}.
    flow = await app.ctx.tams.Flow(request, flow_id)
    flow.has_write(groups, throw=True)

    if tag_name == "auth_classes":
        # Validate has permissions that will be removed
        flow.validate_modify_auth_classes([], groups)

    return await app.ctx.tams.passthrough_request(request)


@app.route('/flows/<flow_id:uuid>/description', methods=['GET', 'HEAD'])
@handle_token()
@passthrough_if_admin()
async def flow_description(request: Request, groups: list[str], flow_id: UUID):
    # Request must have read permissions on {flowID}.
    (await app.ctx.tams.Flow(request, flow_id)).has_read(groups, throw=True)
    return await app.ctx.tams.passthrough_request(request)


@app.route('/flows/<flow_id:uuid>/description', methods=['PUT', 'DELETE'])
@handle_token()
@passthrough_if_admin()
async def put_del_flow_description(request: Request, groups: list[str], flow_id: UUID):
    # Request must have write permissions on {flowId}.
    (await app.ctx.tams.Flow(request, flow_id)).has_write(groups, throw=True)
    return await app.ctx.tams.passthrough_request(request)


@app.route('/flows/<flow_id:uuid>/label', methods=['GET', 'HEAD'])
@handle_token()
@passthrough_if_admin()
async def flow_label(request: Request, groups: list[str], flow_id: UUID):
    # Request must have read permissions on {flowID}.
    (await app.ctx.tams.Flow(request, flow_id)).has_read(groups, throw=True)
    return await app.ctx.tams.passthrough_request(request)


@app.route('/flows/<flow_id:uuid>/label', methods=['PUT', 'DELETE'])
@handle_token()
@passthrough_if_admin()
async def put_del_flow_label(request: Request, groups: list[str], flow_id: UUID):
    # Request must have write permissions on {flowId}.
    (await app.ctx.tams.Flow(request, flow_id)).has_write(groups, throw=True)
    return await app.ctx.tams.passthrough_request(request)


@app.route('/flows/<flow_id:uuid>/read_only', methods=['GET', 'HEAD'])
@handle_token()
@passthrough_if_admin()
async def flow_read_only(request: Request, groups: list[str], flow_id: UUID):
    # Request must have read permissions on {flowID}.
    (await app.ctx.tams.Flow(request, flow_id)).has_read(groups, throw=True)
    return await app.ctx.tams.passthrough_request(request)


@app.route('/flows/<flow_id:uuid>/read_only', methods=['PUT'])
@handle_token()
@passthrough_if_admin()
async def put_flow_read_only(request: Request, groups: list[str], flow_id: UUID):
    # Request must have write permissions on {flowId}.
    (await app.ctx.tams.Flow(request, flow_id)).has_write(groups, throw=True)
    return await app.ctx.tams.passthrough_request(request)


@app.route('/flows/<flow_id:uuid>/flow_collection', methods=['GET', 'HEAD'])
@handle_token()
@passthrough_if_admin()
async def flow_collection(request: Request, groups: list[str], flow_id: UUID):
    # Request must have read permissions on {flowID}.
    (await app.ctx.tams.Flow(request, flow_id)).has_read(groups, throw=True)
    return await app.ctx.tams.passthrough_request(request)


@app.route('/flows/<flow_id:uuid>/flow_collection', methods=['PUT', 'DELETE'])
@handle_token()
@passthrough_if_admin()
async def put_del_flow_collection(request: Request, groups: list[str], flow_id: UUID):
    # Request must have write permissions on {flowId}.
    (await app.ctx.tams.Flow(request, flow_id)).has_write(groups, throw=True)
    return await app.ctx.tams.passthrough_request(request)


@app.route('/flows/<flow_id:uuid>/max_bit_rate', methods=['GET', 'HEAD'])
@handle_token()
@passthrough_if_admin()
async def flow_max_bit_rate(request: Request, groups: list[str], flow_id: UUID):
    # Request must have read permissions on {flowID}.
    (await app.ctx.tams.Flow(request, flow_id)).has_read(groups, throw=True)
    return await app.ctx.tams.passthrough_request(request)


@app.route('/flows/<flow_id:uuid>/max_bit_rate', methods=['PUT', 'DELETE'])
@handle_token()
@passthrough_if_admin()
async def put_del_flow_max_bit_rate(request: Request, groups: list[str], flow_id: UUID):
    # Request must have write permissions on {flowId}.
    (await app.ctx.tams.Flow(request, flow_id)).has_write(groups, throw=True)
    return await app.ctx.tams.passthrough_request(request)


@app.route('/flows/<flow_id:uuid>/avg_bit_rate', methods=['GET', 'HEAD'])
@handle_token()
@passthrough_if_admin()
async def flow_avg_bit_rate(request: Request, groups: list[str], flow_id: UUID):
    # Request must have read permissions on {flowID}.
    (await app.ctx.tams.Flow(request, flow_id)).has_read(groups, throw=True)
    return await app.ctx.tams.passthrough_request(request)


@app.route('/flows/<flow_id:uuid>/avg_bit_rate', methods=['PUT', 'DELETE'])
@handle_token()
@passthrough_if_admin()
async def put_del_flow_avg_bit_rate(request: Request, groups: list[str], flow_id: UUID):
    # Request must have write permissions on {flowId}.
    (await app.ctx.tams.Flow(request, flow_id)).has_write(groups, throw=True)
    return await app.ctx.tams.passthrough_request(request)


@app.route('/flows/<flow_id:uuid>/segments', methods=['GET', 'HEAD'])
@handle_token()
@passthrough_if_admin()
async def flow_segments(request: Request, groups: list[str], flow_id: UUID):
    # Request must have read permissions on {flowID}.
    (await app.ctx.tams.Flow(request, flow_id)).has_read(groups, throw=True)
    return await app.ctx.tams.passthrough_request(request)


@app.route('/flows/<flow_id:uuid>/segments', methods=['POST'])
@handle_token()
@passthrough_if_admin()
async def post_flow_segments(request: Request, groups: list[str], flow_id: UUID):
    # Request must have write permissions on {flowId},
    # and either this must be the first registration of the Media Object(s) (i.e. /objects/{objectId} returns 404)
    # or the request must have read access to the Media Object(s) being written.
    # Otherwise reject.
    (await app.ctx.tams.Flow(request, flow_id)).has_write(groups, throw=True)

    # Note: The following for-loop is quite inefficient and potentially slow.
    # While the use of asyncio in this implementation allows for requests to be
    # processed in parallel, the items in this for-loop will be processed sequentially
    # but without blocking. A complete implementation may wish to parallelise this
    # loop. This hasn't been done here to help with readability.
    segments = request.json
    if type(segments) is not list:
        segments = [segments]
    for segment in segments:
        object_id = segment.get("object_id", None)
        if not object_id:
            raise InvalidUsage("Missing segments `object_id`")

        media_object = await app.ctx.tams.MediaObject(request, object_id)

        if media_object.exists:
            try:
                await media_object.has_read(groups, throw=True)
            except NotFound, Forbidden:
                raise InvalidUsage(f"Object {object_id} not found")

    return await app.ctx.tams.passthrough_request(request)


@app.route('/flows/<flow_id:uuid>/segments', methods=['DELETE'])
@handle_token()
@passthrough_if_admin()
async def del_flow_segments(request: Request, groups: list[str], flow_id: UUID):
    # Request must have delete permissions on {flowId}.
    (await app.ctx.tams.Flow(request, flow_id)).has_delete(groups, throw=True)
    return await app.ctx.tams.passthrough_request(request)


@app.route('/flows/<flow_id:uuid>/storage', methods=['POST'])
@handle_token()
@passthrough_if_admin()
async def post_flow_storage(request: Request, groups: list[str], flow_id: UUID):
    # Request must have write permissions on {flowId}.
    (await app.ctx.tams.Flow(request, flow_id)).has_write(groups, throw=True)
    return await app.ctx.tams.passthrough_request(request)


@app.route('/objects/<object_id:uuid>', methods=['GET', 'HEAD'])
@handle_token()
@passthrough_if_admin()
async def object(request: Request, groups: list[str], object_id: UUID):
    # Restrict returned data in referenced_by_flows property to only the Flows that the request has read access to.
    # If the request has read access to no Flows of this object, return 404,
    # however if the request has access but all of the Flows have been filtered out,
    # return the response with an empty referenced_by_flows list.
    await (await app.ctx.tams.MediaObject(request, object_id)).has_read(groups, throw=True)
    return await app.ctx.tams.filtered_object(request, object_id, groups)


@app.route('/objects/<object_id:uuid>/instances', methods=['POST', 'DELETE'])
@handle_token()
@passthrough_if_admin()
async def post_del_object_instances(request: Request, groups: list[str], object_id: UUID):
    # Request must have write permissions on {objectId}.
    await (await app.ctx.tams.MediaObject(request, object_id)).has_write(groups, throw=True)
    return await app.ctx.tams.passthrough_request(request)


@app.route('/flow-delete-requests', methods=['HEAD', 'GET'])
@handle_token()
@passthrough_if_admin()
async def flow_delete_requests(auth_request: Request, groups):
    # Admin only
    raise NotFound()


@app.route('/flow-delete-requests/<request_id:uuid>', methods=['HEAD', 'GET'])
@handle_token()
@passthrough_if_admin()
async def flow_delete_request(request: Request, groups: list[str], request_id: UUID):
    # Request must have delete permissions on the Delete Request's Flow ID.
    # NOTE: This implementation will only work with TAMS Service implementations that
    # continue to return Flow metadata while the Flow is being deleted.
    # Partial deletes should work with all implementations

    # Needs to be a GET to retrieve `flow_id`
    flow_delete_request_res = await app.ctx.tams.get_upstream(request, f"flow-delete-requests/{request_id}")
    flow_id = flow_delete_request_res.json["flow_id"]
    (await app.ctx.tams.Flow(request, flow_id)).has_delete(groups, throw=True)

    # Handle both GET & HEAD
    return await app.ctx.tams.passthrough_request(request)


if __name__ == "__main__":
    app.run(access_log=True)
