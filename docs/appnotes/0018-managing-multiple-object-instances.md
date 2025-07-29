# 0018: Managing Multiple Object Instances

## Abstract

[ADR0038](../adr/0038-improved-storage-management.md) added the ability to create multiple managed copies of the same Media Object in the same TAMS instance.
This application note describes how a client may create, reference, duplicate, and delete instances of a Media Object.
It also describes potential security considerations for deployments.

## Managing Multiple Object Instances

### Initial Object Creation

When a Media Object is initially created, it must be allocated storage against a specific Flow.
This is so that the Media Object may inherit permissions and its MIME Type from the Flow.

A request is made to [`/flows/{flowId}/storage`](https://bbc.github.io/tams/7.0/index.html#/operations/POST_flows-flowId-storage) with the `limit` property set to the number of Media Object storage locations required.
If a specific Storage Backend is required, or if the service instance does not provide a default, a `storage_id` may also be specified.
Available Storage Backends, and defaults, are advertised at the [`/service/storage-backends`](https://bbc.github.io/tams/7.0/index.html#/operations/GET_storage-backends) endpoint.

Example POST body to `/flows/{flowId}/storage`:

```json
{
  "limit": 1,
  "storage_id": "60af2ab4-e8a5-4c65-a09b-d35983680315"
}
```

Example response:

```json
{
  "pre": [
    {
      "action": "create_bucket",
      "bucket_id": "tams-e2b89b02-21e7-5f9d-aa2d-db38b01453c9",
      "put_url": {
        "url": "https://example.store.com/tams-e2b89b02-21e7-5f9d-aa2d-db38b01453c9?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=0&X-Amz-Date=20230316T120329Z&X-Amz-Expires=300&X-Amz-SignedHeaders=host&X-Amz-Signature=0",
        "body": "<CreateBucketConfiguration xmlns=\"http://s3.amazonaws.com/doc/2006-03-01/\">\n    <LocationConstraint>default</LocationConstraint>\n</CreateBucketConfiguration >\n"
      }
    }
  ],
  "media_objects": [
    {
      "object_id": "tams-e2b89b02-21e7-5f9d-aa2d-db38b01453c9/846023d3-612d-5014-bc47-88f6eb2d04bb",
      "put_url": {
        "url": "https://example.store.com/tams-e2b89b02-21e7-5f9d-aa2d-db38b01453c9/846023d3-612d-5014-bc47-88f6eb2d04bb?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=0&X-Amz-Date=20230316T120329Z&X-Amz-Expires=300&X-Amz-SignedHeaders=content-type%3Bhost&X-Amz-Signature=0",
        "content-type": "video/mp2t"
      }
    }
  ]
}
```

In the response above, you can see a "pre" action alongside the the Media Object.
This may be returned where a service implementation maintains multiple buckets on a storage backend.
There is no requirement for a client to use all Media Objects they request.
This allows a client to request allocation of Objects in bulk, improving efficiency.
But it also means that a bucket could be created and not used.
This could result in users incurring unnecessary costs.
A service may therefore require the client to trigger its creation.
Note that the request may include pre-actions for multiple buckets.
The bucket a Media Object is associated with is pre-fixed to the `object_id`.
As such, the client should only run the pre-action for a given bucket when it first wishes to populate a Media Object in that bucket.

In the example above, a client would first trigger the creation of the bucket by a PUT request to the specified pre-signed URL with the specified body.
The client would then PUT the Media Object's file to the `put_url` for one of the Media Object's in the list, with the `content-type` on the request set to the specified value.

Once the media Object has been uploaded, it should be registered on the Flow's timeline via a Segment.
The appropriate Object ID from the requests above, and the Timerange it covers should be registered via a POST request to the [`/flows/{flowId}/segments`](https://bbc.github.io/tams/7.0/index.html#/operations/POST_flows-flowId-segments) endpoint.

Example POST body to `/flows/{flowId}/segments`:

```json
{
  "object_id": "tams-e2b89b02-21e7-5f9d-aa2d-db38b01453c9/846023d3-612d-5014-bc47-88f6eb2d04bb",
  "timerange": "[20:0_21:0)"
}
```

Note that the first time a Media Object is registered against a Flow Segment, the Flow ID of the Flow Segment MUST match the one the storage was allocated against.
i.e. The `flowId` MUST match in `/flows/{flowId}/storage` and `/flows/{flowId}/segments`.
This is to enable the correct inheritance of permissions and content-type.

The Flow Segment making use of the Media Object will now be available for reading at [`/flows/{flowId}/segments`](https://bbc.github.io/tams/7.0/index.html#/operations/GET_flows-flowId-segments).

### Referencing an Existing Object

After initial registration with a Flow, a Media Object may be referenced by other Flows.
The client adding a reference to the existing Object MUST have read permissions on a Flow which already references the Object, and write permissions on the destination Flow.
For example, a client with read access to a Flow with ID `{flowId}` and write permissions on a Flow with ID `{flowId2}` may re-use Objects from `{flowId}` in `{flowId2}`.

Example POST body to `/flows/{flowId2}/segments`:

```json
{
  "object_id": "tams-e2b89b02-21e7-5f9d-aa2d-db38b01453c9/846023d3-612d-5014-bc47-88f6eb2d04bb",
  "timerange": "[165:0_166:0)",
  "ts_offset": "145:0"
}
```

Note the `ts_offset` which describes the difference between the timing internal to the media, and the Flow timeline.
The Segment above in `flowId` used the default `ts_offset` of `0:0`.
As the Segment it was used in in `flowId` started at `20:0`, but in `flowId2` it is placed at `165:0`, we must set a `ts_offset` of `145:0`.
For more information on `ts_offset`, see [here](https://bbc.github.io/tams/7.0/index.html#/operations/GET_flows-flowId-segments).

### Duplicating an Existing Object (Client Managed)

There are many reasons a client may want to create a duplicate instance of a Media Object.
To create a backup.
To create copies that are physically or logically closer to other systems.
To move content to archive storage.
All while being able to refer to the this collection of duplicates with the same Media Object ID in Flow Segments.

There are two methods of creating duplicate instances of a Media Object.
The first requires the client to manage the duplication process.

The client first has to allocate additional storage to the Media Object on the required Storage Backend.
This is done via a POST to `/objects/{objectId}/storage` with the required `storage_id`.

Example POST body to `/objects/{objectId}/storage`:

```json
{
  "storage_id": "323367fd-21bb-4f2e-ad38-faf048c4ccfc"
}
```

The response is identical in form to the `/flows/{flowId}/storage` response above:

```json
{
  "pre": [
    {
      "action": "create_bucket",
      "bucket_id": "tams-c6b8e7cc-edd3-5f6d-9d79-4467d06eb8bf",
      "put_url": {
        "url": "https://example.store.com/tams-c6b8e7cc-edd3-5f6d-9d79-4467d06eb8bf?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=0&X-Amz-Date=20230316T120329Z&X-Amz-Expires=300&X-Amz-SignedHeaders=host&X-Amz-Signature=0",
        "body": "<CreateBucketConfiguration xmlns=\"http://s3.amazonaws.com/doc/2006-03-01/\">\n    <LocationConstraint>default</LocationConstraint>\n</CreateBucketConfiguration >\n"
      }
    }
  ],
  "media_objects": [
    {
      "object_id": "tams-c6b8e7cc-edd3-5f6d-9d79-4467d06eb8bf/846023d3-612d-5014-bc47-88f6eb2d04bb",
      "put_url": {
        "url": "https://example.store.com/tams-c6b8e7cc-edd3-5f6d-9d79-4467d06eb8bf/846023d3-612d-5014-bc47-88f6eb2d04bb?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=0&X-Amz-Date=20230316T120329Z&X-Amz-Expires=300&X-Amz-SignedHeaders=content-type%3Bhost&X-Amz-Signature=0",
        "content-type": "video/mp2t"
      }
    }
  ]
}
```

Once the media has been uploaded to the new Storage Backend, it must be registered as available.
This is done via a POST to `/objects/{objectId}/instances` with the `storage_id`.

Example POST body to `/objects/{objectId}/instances`:

```json
{
  "storage_id": "323367fd-21bb-4f2e-ad38-faf048c4ccfc"
}
```

The available instances of the Media Object will now be advertised in `get_urls` on the `/objects/{objectId}` endpoint and on the `/flows/{flowId}/segments` for all Flow Segments which use the Media Object.

### Duplicating an Existing Object (Server Managed)

Some TAMS implementations may support a second, server managed, method of duplicating Media Objects.

For this method, clients POST the required `storage_id` to `/objects/{objectId}/instances`.
This is the same as the final step in the client managed approach.
The TAMS instance will identify that it has not previously allocated storage for the requested Media Object on the requested Storage Backend.
It will allocate storage, and populate it from an existing copy of the Media Object.
It will then begin advertising the copy in `get_urls` lists.

Example POST body to `/objects/{objectId}/instances`:

```json
{
  "storage_id": "323367fd-21bb-4f2e-ad38-faf048c4ccfc"
}
```

### Deleting an Object Instance

Specific instances of a Media Object can be deleted by a DELETE request to `/objects/{objectId}/get_urls` with the relevant `storage_id` in the query string.

Example DELETE request:

```text
http://tams.example.com/objects/846023d3-612d-5014-bc47-88f6eb2d04bb/get_urls?storage_id=323367fd-21bb-4f2e-ad38-faf048c4ccfc
```

Once deleted, this instance will no longer be advertised in `get_urls` on the `/objects/{objectId}` endpoint or on the `/flows/{flowId}/segments` for Flow Segments which use the Media Object.

## Deployment Considerations

### Security

The approach to supporting multiple Media Object instances in TAMS enables efficient re-use of media, changing ownership through the lifecycle of the media, and self-service re-location of media to meet the purposes of individual users
With this increased flexibility comes the potential for new attack vectors for malicious actors.

Consider a Flow A with its Media Objects.
A malicious actor has read access to Flow A, but not read access.
The actor creates a new Flow, Flow B, and re-uses Media Objects from Flow A in Flow B.
The write permissions they have on Flow B allows them to add new instances to the Objects.
The malicious actor creates new malicious instances and adds them to the Objects.
Users of Flow A are now presented with the malicious instances, in addition to the original ones, on Flow A's Segments.

This attack vector can be mitigated in multiple ways.

The TAMS instance's authorisation logic may be configured to only allow those with write access to the original Flow A to add new instances.
This mitigates the attack vector described, but places more of a burden on the original owner to manage creation/deletion of duplicate instances.

The TAMS instance may be configured to only allow managed duplication.
This guarantees all instances will be identical and removes the ability for malicious instances to be uploaded by the actor.

An organisation may, of course, also assess and accept the risk associated with allowing user-managed duplication of Media Objects.
