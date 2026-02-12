import dataclasses
import json
from uuid import UUID
from copy import deepcopy
from typing import Any, Callable, cast, Optional, List, Dict

from httpx import AsyncClient
from sanic.exceptions import Forbidden, NotFound, InvalidUsage
from sanic.request import Request
from sanic.response import raw as raw_resp
from sanic.response import json as json_resp
from sanic.response.types import HTTPResponse
from logging import Logger

from permissions import any_is_read, any_is_write, any_is_delete, any_is_any, filter_read, filter_write, filter_delete


@dataclasses.dataclass
class Tams(object):
    client: AsyncClient
    logger: Logger
    api_url: str

    async def Flow(self, request: Request, flow_id: UUID):
        return await Flow(self.client, self.api_url, request, flow_id)._async_init()

    async def Source(self, request: Request, source_id: UUID):
        return await Source(self.client, self.api_url, request, source_id)._async_init()

    async def Webhook(self, request: Request, webhook_id: UUID):
        return await Webhook(self.client, self.api_url, request, webhook_id)._async_init()

    async def MediaObject(self, request: Request, object_id: UUID):
        return await MediaObject(self.client, self.api_url, request, object_id)._async_init()

    async def passthrough_request(self, request: Request) -> HTTPResponse:
        if request.path == "":
            target_url = self.api_url
        else:
            target_url = f"{self.api_url}{request.path}"

        self.logger.info(f"Proxying {request.method} request to {request.path} -> {target_url}")

        # Suppress any HTML render, since the links won't work
        if "accept" in request.headers:
            del (request.headers["accept"])

        if "content-length" in request.headers:
            del (request.headers["content-length"])

        res = await self.client.request(
            method=request.method,
            headers=request.headers,
            url=target_url,
            json=request.json,
            params=request.args
        )

        if res.status_code == 301 or res.status_code == 302:
            # Rewrite the location header to avoid redirecting upstream
            assert request.conn_info
            original_server = request.conn_info.server
            protocol = "https" if request.conn_info.ssl else "http"
            original_origin = f"{protocol}://{original_server}"
            res.headers["Location"] = res.headers["Location"].replace(self.api_url, original_origin)

        return raw_resp(res.text, res.status_code, cast(dict[str, str], res.headers))

    async def get_upstream(self, request: Request, url: str, params: Optional[dict] = None) -> Any:
        headers_copy = deepcopy(request.headers)
        if "content-length" in headers_copy:
            del (headers_copy["content-length"])

        return await self.client.request(
            method="GET",
            headers=headers_copy,
            url=f"{self.api_url}{url}",
            params=params
        )

    async def _filtered_resource_listing(self, request: Request, groups: list[str]) -> HTTPResponse:
        # First request the resources of this type the user has access to
        orig_auth_classes_str = request.args.get("tag.auth_classes", "")
        orig_auth_classes = orig_auth_classes_str.split(",") if orig_auth_classes_str else []
        request.args["tag.auth_classes"] = ",".join(groups)

        res = await self.passthrough_request(request)

        json_body = json.loads(res.body) if res.body else None

        filtered_body: Any = []

        # Handle user specified filter on `auth_classes`
        if len(orig_auth_classes) > 0 and (type(json_body) is list):
            for item in json_body:
                # Note: This could return empty lists before the last page
                # A more complete implementation could recurse
                auth_classes = item.get("tags", {}).get("auth_classes", [])
                if set(auth_classes).intersection(orig_auth_classes):
                    filtered_body.append(item)
        else:
            filtered_body = json_body

        return json_resp(filtered_body, res.status, cast(dict[str, str], res.headers))

    async def filtered_sources(self, request: Request, groups: list[str]) -> HTTPResponse:
        return await self._filtered_resource_listing(request, groups)

    async def filtered_flows(self, request: Request, groups: list[str]) -> HTTPResponse:
        return await self._filtered_resource_listing(request, groups)

    async def filtered_webhooks(self, request: Request, groups: list[str]) -> HTTPResponse:
        return await self._filtered_resource_listing(request, groups)

    async def filtered_object(self, request: Request, object_id: UUID, groups: list[str]) -> HTTPResponse:
        orig_auth_classes_str = request.args.get("tag.auth_classes", "")
        orig_auth_classes = orig_auth_classes_str.split(",") if orig_auth_classes_str else []

        request.args["tag.auth_classes"] = ",".join(groups)

        res = await self.passthrough_request(request)

        assert res.body
        json_body = json.loads(res.body)

        filtered_referenced_by_flows = []

        # Handle user specified filter on `auth_classes`
        if len(orig_auth_classes) > 0:
            for flow in json_body["referenced_by_flows"]:
                flow = await self.Flow(request, flow)
                if flow.has_any(orig_auth_classes):
                    filtered_referenced_by_flows.append(flow)
        else:
            filtered_referenced_by_flows = json_body["referenced_by_flows"]

        json_body["referenced_by_flows"] = filtered_referenced_by_flows

        return json_resp(json_body, res.status, cast(dict[str, str], res.headers))

    async def validate_webhook(self, request: Request, groups: list[str]):
        # Validates webhook based on permissions

        # Reject wildcard webhooks
        events = request.json.get("events", [])
        if any(event.startswith("flows/") for event in events):
            if (
              not request.json.get("flow_ids", [])
              and not request.json.get("source_ids", [])
              and not request.json.get("flow_collected_by_ids", [])
              and not request.json.get("source_collected_by_ids", [])):
                raise InvalidUsage(
                    "When subscribing to Flow events, one or more of 'flow_ids', "
                    "'source_ids', 'flow_collected_by_ids', and 'source_collected_by_ids' must be specified")

        if any(event.startswith("sources/") for event in events):
            if not request.json.get("source_ids", []) and not request.json.get("source_collected_by_ids", []):
                raise InvalidUsage("When subscribing to Source events, one or both of "
                                   "'source_ids' and 'source_collected_by_ids' must be specified")

        # If any filter Flows are invalid, reject immediately
        combined_flow_ids = (set(request.json.get("flow_ids", []))
                             | set(request.json.get("flow_collected_by_ids", [])))
        for flow_id in combined_flow_ids:
            if not (await self.Flow(request, flow_id)).has_read(groups):
                raise InvalidUsage("One or more filter Flow IDs don't exist or have insufficient permissions")

        # If any filter Sources are invalid, reject immediately
        combined_source_ids = (set(request.json.get("source_ids", []))
                               | set(request.json.get("source_collected_by_ids", [])))
        for source_id in combined_source_ids:
            if not (await self.Source(request, source_id)).has_read(groups):
                raise InvalidUsage("One or more filter Source IDs don't exist or have insufficient permissions")

    def decode_link_header(self, link_header: str) -> List[Dict[str, Any]]:
        processed_links = []
        working_links = link_header.split(",")
        for working_link in working_links:
            parts = working_link.split(";")
            url = parts[0].strip().lstrip("<").rstrip(">")

            link_params = {}
            for working_param in parts[1:]:
                param, val = working_param.strip().split("=", 1)

                # Remove leading/trailing quotation marks
                val = val.split("\"", 1)[-1].rsplit("\"", 1)[0]
                link_params[param] = val

            processed_links.append({
                "url": url,
                "params": link_params
            })

        return processed_links

    async def static_webhook(self, request: Request, groups: list[str]):
        # Generates a staticly computed list of Flows and Sources to subscribe to based on permissions
        # Source/Flow ID filters are applied such that all must be satisfied

        # Statically evaluate Sources to include
        static_sources = set(request.json.get("source_ids", []))

        for source_id in request.json.get("source_collected_by_ids", []):
            res = (await self.get_upstream(request, f"/sources/{source_id}"))
            collected_sources = res.json().get("source_collection", []) if res.status_code == 200 else []
            for collected_source in collected_sources:
                collected_source_id = collected_source["id"]
                if (await self.Source(request, collected_source_id)).has_read(groups):
                    if "source_ids" in request.json:
                        static_sources &= {collected_source_id}
                    else:
                        static_sources.add(collected_source_id)

        # Statically evaluate Flows to include
        static_flows = set(request.json.get("flow_ids", []))

        for flow_id in request.json.get("flow_collected_by_ids", []):
            res = await self.get_upstream(request, f"/flows/{flow_id}/flow_collection")
            collected_flows = res.json() if res.status_code == 200 else []

            for collected_flow in collected_flows:
                collected_flow_id = collected_flow["id"]
                if (await self.Flow(request, collected_flow_id)).has_read(groups):
                    if "flow_ids" in request.json:
                        static_flows &= {collected_flow_id}
                    else:
                        static_flows.add(collected_flow_id)

        # If subscribed to flow events, get flows from sources
        events = request.json.get("events", [])
        if any(event.startswith("flows/") for event in events):
            for source_id in static_sources:
                res = await self.get_upstream(request, "/flows", {"source_id": source_id})
                while True:
                    for flow in res.json():
                        flow_id = flow["id"]
                        if (await self.Flow(request, flow_id)).has_read(groups):
                            if any([x in request.json for x in ["flow_ids", "flow_collected_by_ids"]]):
                                static_flows &= {flow_id}
                            else:
                                static_flows.add(flow_id)

                    # Follow paging links
                    links = self.decode_link_header(res.headers.get("link", ""))
                    for link in links:
                        if link["params"].get("rel", "") == "next":
                            next_link = link["url"]
                            break
                    else:
                        # No "next" link found. Exit while loop.
                        break

                    next_path = next_link.split(self.api_url, 1)[-1]
                    res = await self.get_upstream(request, next_path)

        # Verify flattend list isn't empty
        # This step is really important! If the flattened lists are empty, they will be
        # interpreted as a wildcard match and return data the user shouldn't have access to!
        events = request.json.get("events", [])
        if any(event.startswith("flows/") for event in events):
            if not static_flows:
                raise InvalidUsage("Webhook subscribes to Flow events, but doesn't match any Flow IDs")

        if any(event.startswith("sources/") for event in events):
            if not static_sources:
                raise InvalidUsage("Webhook subscribes to Source events, but doesn't match any Source IDs")

        # Build statically filtered request
        static_body = request.json
        static_body.pop("flow_collected_by_ids", None)
        static_body.pop("source_collected_by_ids", None)
        if static_flows:
            static_body["flow_ids"] = list(static_flows)
        if static_sources:
            static_body["source_ids"] = list(static_sources)

        # Note: We can't use deepcopy() here due to C optimisations in Request
        static_request = Request(
            url_bytes=request.path.encode(),
            headers=request.headers,
            version=request.version,
            method=request.method,
            transport=request.transport,
            app=request.app,
            head=request.head
        )
        # Make sure the signalled encoding matches the new bodies encoding
        static_request.headers["Content-Type"] = "application/json; charset=utf-8"
        static_request.body = json.dumps(static_body).encode("UTF-8")

        return static_request


@dataclasses.dataclass
class Resource(object):
    client: AsyncClient
    api_url: str
    request: Request

    classes: list[str] = dataclasses.field(init=False, repr=False, default_factory=list)
    exists: bool = dataclasses.field(init=False, default=False)

    async def _get_upstream(self, url: str, throw: bool = False) -> Any:
        headers_copy = deepcopy(self.request.headers)
        if "content-length" in headers_copy:
            del (headers_copy["content-length"])

        res = await self.client.request(
            method="GET",
            headers=headers_copy,
            url=f"{self.api_url}/{url}"
        )

        if res.status_code != 200:
            if throw:
                raise NotFound()
            return {}
        else:
            self.exists = True
            return res.json()

    def has_permission(self,
                       check_function: Callable[[list[str]], bool],
                       groups: list[str],
                       throw: bool = False) -> bool:
        if throw and not self.exists:
            raise NotFound()

        has_permission = check_function(list(set(self.classes) & set(groups)))

        if throw and not has_permission:
            self.has_any(groups, throw)  # Will raise NotFound if has no permissions
            raise Forbidden("Insufficient permissions")

        return has_permission

    def has_read(self, groups: list[str], throw: bool = False) -> bool:
        return self.has_permission(any_is_read, groups, throw)

    def has_write(self, groups: list[str], throw: bool = False) -> bool:
        return self.has_permission(any_is_write, groups, throw)

    def has_delete(self, groups: list[str], throw: bool = False) -> bool:
        return self.has_permission(any_is_delete, groups, throw)

    def has_any(self, groups: list[str], throw: bool = False) -> bool:
        if throw and not self.exists:
            raise NotFound()

        has_permission = any_is_any(list(set(self.classes) & set(groups)))

        if throw and not has_permission:
            raise NotFound()

        return has_permission

    def validate_modify_auth_classes(self, new_auth_classes: list[str], groups: list[str]) -> None:
        added_classes = list(set(new_auth_classes) - set(self.classes))
        removed_classes = list(set(self.classes) - set(new_auth_classes))
        changed_classes = list(set(added_classes + removed_classes))

        self.has_write(groups, throw=True)

        if any_is_read(changed_classes):
            self.has_read(groups, throw=True)

        if any_is_delete(changed_classes):
            self.has_delete(groups, throw=True)


class Flow(Resource):
    def __init__(self, client: AsyncClient, api_url: str, request: Request, flow_id: UUID) -> None:
        super().__init__(client, api_url, request)
        self.flow_id = flow_id

    async def _async_init(self):
        _flow_data = await self._get_upstream(f"flows/{self.flow_id}")

        if self.exists:
            self.classes = _flow_data.get("tags", {}).get("auth_classes", [])
            self.source_id = _flow_data["source_id"]

        return self


class Source(Resource):
    def __init__(self, client: AsyncClient, api_url: str, request: Request, source_id: UUID) -> None:
        super().__init__(client, api_url, request)
        self.source_id = source_id

    async def _async_init(self):
        _source_data = await self._get_upstream(f"sources/{self.source_id}")

        if self.exists:
            self.classes = _source_data.get("tags", {}).get("auth_classes", [])
        return self


class Webhook(Resource):
    def __init__(self, client: AsyncClient, api_url: str, request: Request, webhook_id: UUID) -> None:
        super().__init__(client, api_url, request)
        self.webhook_id = webhook_id

    async def _async_init(self):
        _webhook_data = await self._get_upstream(f"service/webhooks/{self.webhook_id}")

        if self.exists:
            self.classes = _webhook_data.get("tags", {}).get("auth_classes", [])
        return self


@dataclasses.dataclass
class MediaObject(object):
    client: AsyncClient
    api_url: str
    request: Request
    object_id: UUID

    exists: bool = dataclasses.field(init=False, default=False)

    async def _get_upstream(self, groups: list[str], throw: bool = False) -> Any:
        headers_copy = deepcopy(self.request.headers)
        if "content-length" in headers_copy:
            del (headers_copy["content-length"])

        args = {"flow_tag.auth_classes": ",".join(groups)}

        res = await self.client.request(
            method="GET",
            headers=headers_copy,
            url=f"{self.api_url}/objects/{self.object_id}",
            params=args
        )

        if res.status_code != 200:
            if throw:
                raise NotFound()
            return {}
        else:
            self.exists = True

            return res.json()

    async def _async_init(self):
        # Prime self.exists
        await self._get_upstream([])

        return self

    async def has_permission(self, groups: list[str], throw: bool = False) -> bool:
        media_object = await self._get_upstream(groups)

        if throw and not self.exists:
            raise NotFound()

        has_permission = (media_object.get("referenced_by_flows", []) != [])

        if throw and not has_permission:
            await self.has_any(groups, throw)  # Will raise NotFound if has no permissions
            raise Forbidden("Insufficient permissions")

        return has_permission

    async def has_read(self, groups: list[str], throw: bool = False) -> bool:
        return await self.has_permission(filter_read(groups), throw)

    async def has_write(self, groups: list[str], throw: bool = False) -> bool:
        return await self.has_permission(filter_write(groups), throw)

    async def has_delete(self, groups: list[str], throw: bool = False) -> bool:
        return await self.has_permission(filter_delete(groups), throw)

    async def has_any(self, groups: list[str], throw: bool = False) -> bool:
        media_object = await self._get_upstream(groups)

        if throw and not self.exists:
            raise NotFound()

        has_permission = (media_object.get("referenced_by_flows", []) != [])

        if throw and not has_permission:
            raise NotFound()

        return has_permission
