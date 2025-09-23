---
status: "accepted"
---
# Improved Storage Management

## Context and Problem Statement

In [ADR0032](./0032-specifying-storage-backend.md), support was added for advertising multiple storage backends, and selecting one when allocating storage against Flows.
The TAMS specification has always had the ability to advertise multiple URLs for retrieving Media Objects.
But, so far, there has not been direct support for creating and managing duplicates of Media Objects under the control of a TAMS instance.

An Objects endpoint was added in [ADR0027](./0027-add-objects-api-endpoint.md) that advertises the Flows where a given Object is referenced.
This has begun a transition from thinking about Objects being heavily tied to a Segment.
And a move from thinking about "Segment reuse" to "Object reuse".
Until now, the TAMS specifcation has been unclear on the ownership of `get_urls` being the Segment or Object.
In particular, whether re-use of an Object should result in `get_urls` and changes to them being reflected across all segments using of them.

This ADR proposes explicitly linking ownership of `get_urls` to Objects, and providing mechanisms for adding and removing controlled and uncontrolled instances of Objects to their `get_urls` list.
This seperation of Objects and Segments does not require breaking changes, but does provide greater clarity in how the specification should be implemented.

## Considered Options

* Option 1a: Manage `get_urls` via the Flows endpoints
* Option 1b: Add `get_urls` management to the Objects endpoint
* Option 2a: Manage additional Object storage via Flow storage endpoint
* Option 2b: Manage additional Object storage via a Objects storage endpoint
* Option 2c: Manage additional Object storage AND initial Object storage via a Objects storage endpoint
* Option 3a: Call Object Instance management endpoint `get_urls`
* Option 3b: Call Object Instance management endpoint `instances`
* Option 4a: Duplicaion of Object Instances is managed by the Server
* Option 4b: Duplicaion of Object Instances is managed by the Client

## Decision Outcome

Chosen options:

* Option 1b: Add `get_urls` management to the Objects endpoint
* Option 2b: Manage additional Object storage via a Objects storage endpoint
* Option 3b: Call Object Instance management endpoint `instances`
* Option 4a: Duplicaion of Object Instances is managed by the Server

These options have been chosen because they provide clearer boundaries between Media Objects and Segments in the data model and its implementation.
They should avoid confusion arrising from changes to one Flow impacting another.
And they minimise un-needed changes to the API and common workflows.
Option 4a also minamises potential new attack vectors.

### Implementation

Implemented by <https://github.com/bbc/tams/pull/144>

## Pros and Cons of the Options

### Option 1a: Manage `get_urls` via the Flows endpoints

This option would see us add support for in-place editing of `get_urls` and see the edits propagated to other segments making use of the same Media Object.

* Good, because it somewhat matches existing patterns for updating `get_urls`
* Good, because it would remove a race condition of the delete & re-create pattern with Object garbage-collection in implementations
* Bad, because changes to one Flow's segment may have an impact on other's
* Bad, because it persists a blurring of Segments and Media Objects in the TAMS data model

### Option 1b: Add `get_urls` management to the Objects endpoint

This option would see HTTP methods added to/under the `/objects` endpoint to facilitate management of `get_urls`.

* Good, because it would remove a race condition of the delete & re-create pattern with Object garbage-collection in implementations
* Good, because it provides a clearer boundary between Media Objects and Segments
* Good, because edits are performed on the shared Media Objects, rather than as side affects between Flows
* Neutral, because it requires the replacement of a "delete & re-create" pattern with for-purpose endpoints

### Option 2a: Manage additional Object storage via Flow storage endpoint

The existing endpoint used for allocation of storage, which a client will upload media to, is under the `/flows/{flowId}` endpoint at `/flows/{flowId}/storage`.
This is because storage needs to be tied to a specific Flow initially so it can inherit permissions from that Flow, and so the correct MIME type may be obtained and applied to the object on the object storage backend.

This option would see storage for additional instances of a Media Object be allocated via the existing endpoint.

* Good, because it makes use of an existing endpoint and workflows
* Good, because it reduces required changes to the API
* Bad, because it persists a blurring of Segments and Media Objects in the TAMS data model
* Bad, because the allocation of storage against one flow, that may then be used by many could be confusing
* Bad, because it poorly communicates the shared management of Objects
  * It may result in confusion where a client can edit properties of the Object in one location (e.g. Flow A's Segments), but not another (e.g. Flow B's Segments)

### Option 2b: Manage additional Object storage via a Objects storage endpoint

This option would see storage for additional instances of a Media Object be allocated via a new endpoint under the `/objects` endpoint.
Initial allocation would still be performed at `/flows/{flowId}/storage` for the reasons stated above.

* Good, because it provides a clearer boundary between Media Objects and Segments
* Good, because addition of further Object instances is performed on the shared Media Objects, rather than as side affects between Flows
* Good, because it better communicates the shared management of Objects
* Neutral, because it requires new endpoints on the API
* Neutral, because it results in two endpoints for allocating storage, but for different purposes

### Option 2c: Manage additional Object storage AND initial Object storage via a Objects storage endpoint

This would see Option 2b extended such that all storage allocation happens under the `/objects` endpoint.
Allocation of storage via `/flows/{flowId}/storage` would be deprecated/removed.

* Good, because it provides a clearer boundary between Media Objects and Segments
* Good, because it would provide a single endpoint for storage management
* Neutral, because it would require a new mechanism for conveying the initial Flow to inherit permissions and MIME type from
* Neutral, because it requires new endpoints on the API
* Bad, because it would be a breaking change to a core part of the API
* Bad, because it results in two endpoints for allocating storage for the same purpose
* Bad, because it poorly communicates the shared management of Objects

### Option 3a: Call Object Instance management endpoint `get_urls`

Where Option 1b is chosen, we would need to decide on a name for the new Objects endpoint.
As the purpose of this endpoint is to add/remove instances in the `get_urls` list, one option is to title the endpoint `get_urls`.

* Good, because it matches the name of the property it affects
* Bad, because some instances may map to multiple URLs
  * e.g. pre-signed/non-pre-signed variants of URLs
* Bad, because URLs may be generated by instances when retrieved
  * e.g. pre-signed URLs
  * This means the property being PUT/POSTed to the new endpoint doesn't directly match those in the list

### Option 3b: Call Object Instance management endpoint `instances`

Another option is to title the endpoint `instances`.

* Good, because it could avoid confusion over the one-to-many relationship of instances and URLs
* Good, becuase it more clearly conveys that the client manages the instance, but the service manages the URL
* Neutral, because it doesn't match the name of the property it affects

### Option 4a: Duplicaion of Object Instances is managed by the Server

This option would see client's request duplication of an Object to a new Storage Backend, and for that duplication to be carried out by the Server.

* Good, because it requires minimal HTTP requests
* Good, because it ensures the copy is identical to the originating Instance
* Good, because it allows use of efficient copy mechanisms on storage backends
* Neutral, because it requires the server to carry out a task beyond processing metadata
  * Given many object stores support duplication via a single request, it is likely to be more simple and efficient to implement and process than creating multiple pre-signed URLs, verifying Objects have been allocated on a given Storage Backend when registering, etc.
* Neutral, because it doesn't follow existing patterns for Object upload
  * Though those patterns are for a subtly different purpose

### Option 4b: Duplicaion of Object Instances is managed by the Client

This option would see a similar pattern to the existing one for initial creation of objects used for duplication.
Clients would request storage allocation, upload the Media Object to that new location, and then register its availability with the server.

* Good, because it follows existing patterns
* Neutral, because it only requires the server to carry out metadata management
  * Though this may require more a complex implementation in practice
* Bad, because it requires more HTTP requests that Option 4a
* Bad, because it presents a potential attack vector
  * A malicious actor could upload a maliciously crafted Object which doesn't match the original for it to be advertised against existing segments
* Bad, because it prevents the use of efficient object duplication methods present on some object stores
