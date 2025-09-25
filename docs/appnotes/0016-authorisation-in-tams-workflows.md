# 0016: Authorisation in TAMS Workflows

## Abstract

Media workflows often contain sensitive or high-value content, and media organisations need to effectively manage access to that content across their estate.
That requires suitable approaches across both authentication (identifying the user) as discussed in [ADR0028](../adr/0028-authentication-methods.md), and also authorisation (deciding what the user can do), which is discussed in [ADR035](../adr/0035-fine-grained-auth.md) and implemented here.
In general, service implementations, and the organisations that deploy them, are free to define how the authorisation model works based on their needs, however this Application Note provides some guidelines and a starting point.
It is recommended to follow these guidelines where possible to aid in interoperability between TAMS components.

## Overall Principles

Implementers should consider the material they need to protect, the nature of their business and their threat model when deciding how to build authorisation into TAMS-based media workflows.

For some organisations a coarse-grained approach is sufficient: for example allowing groups of users to have read- or write-access to a service instance or large blocks of content.
This might be appropriate for example in a newsroom, where staff are deliberately enabled to work together and access each other's material.

Conversely a finer-grained approach may be required, where specific rules and policies are applied to each piece of content, and groups of users are carefully managed.
This may be appropriate for example when working with a large number of third parties and freelancers in drama production, or when managing a large media archive of high-value content.
It may also be necessary to consider the context of a request: for example whether it originated from a managed device (such as an ingester or edit suite in a facility), from a particular network or in a particular setting: in some cases it may be appropriate to create "machine users" with broader permssions, and in others to have the user work interactively, using their own credentials.

> [!NOTE]
> Throughout this document the term "user" is used as a shorthand for all security principals, including human users, machine accounts, third-party SaaS integrations, etc.

## Coarse Grained Authorisation

A simple approach is to define permissions that apply to an entire TAMS instance at a very coarse level, and use Role-based Access Control (RBAC) to grant access through those permissions.
In RBAC, each action is restricted to users holding a certain role, and users are assigned the relevant roles they need.

These are the recommended permissions (or "scopes" in OAuth 2.0):

| Endpoint                             | Method          | `tams-api/admin` | `tams-api/read` | `tams-api/write` | `tams-api/delete` |
| ------------------------------------ | --------------- | ---------------- | --------------- | ---------------- | ----------------- |
| `/`                                  | `HEAD`/`GET` ⚠️ | ✅               | ✅              | ✅               | ✅               |
| `/service`                           | `HEAD`/`GET` ⚠️ | ✅               | ✅              | ✅               | ✅               |
|                                      | `POST`       ⚠️ | ✅               |                 |                  |                  |
| `/service/storage-backends`          | `HEAD`/`GET` ⚠️ | ✅               | ✅              | ✅               | ✅               |
| `/service/webhooks`                  | `HEAD`/`GET`    | ✅               | ✅              |                  |                  |
|                                      | `POST`          | ✅               |                 | ✅               |                  |
| `/service/webhooks/{webhookId}`      | `HEAD`/`GET`    | ✅               | ✅              |                  |                  |
|                                      | `PUT`        ⚠️ | ✅               | ✅              |                  |                  |
|                                      | `DELETE`     ⚠️ | ✅               | ✅              |                  |                  |
| `/sources`                           | `HEAD`/`GET`    | ✅               | ✅              |                  |                  |
| `/sources/{sourceId}`                | `HEAD`/`GET`    | ✅               | ✅              |                  |                  |
| `/sources/{sourceId}/tags`           | `HEAD`/`GET`    | ✅               | ✅              |                  |                  |
| `/sources/{sourceId}/tags/{name}`    | `HEAD`/`GET`    | ✅               | ✅              |                  |                  |
|                                      | `PUT`           | ✅               |                 | ✅               |                  |
|                                      | `DELETE`     ⚠️ | ✅               |                 | ✅               |                  |
| `/sources/{sourceId}/description`    | `HEAD`/`GET`    | ✅               | ✅              |                  |                  |
|                                      | `PUT`           | ✅               |                 | ✅               |                  |
|                                      | `DELETE`     ⚠️ | ✅               |                 | ✅               |                  |
| `/sources/{sourceId}/label`          | `HEAD`/`GET`    | ✅               | ✅              |                  |                  |
|                                      | `PUT`           | ✅               |                 | ✅               |                  |
|                                      | `DELETE`     ⚠️ | ✅               |                 | ✅               |                  |
| `/flows`                             | `HEAD`/`GET`    | ✅               | ✅              |                  |                  |
| `/flows/{flowId}`                    | `HEAD`/`GET`    | ✅               | ✅              |                  |                  |
|                                      | `PUT`           | ✅               |                 | ✅               |                  |
|                                      | `DELETE`        | ✅               |                 |                  | ✅               |
| `/flows/{flowId}/tags`               | `HEAD`/`GET`    | ✅               | ✅              |                  |                  |
| `/flows/{flowId}/tags/{name}`        | `HEAD`/`GET`    | ✅               | ✅              |                  |                  |
|                                      | `PUT`           | ✅               |                 | ✅               |                  |
|                                      | `DELETE`     ⚠️ | ✅               |                 | ✅               |                  |
| `/flows/{flowId}/description`        | `HEAD`/`GET`    | ✅               | ✅              |                  |                  |
|                                      | `PUT`           | ✅               |                 | ✅               |                  |
|                                      | `DELETE`     ⚠️ | ✅               |                 | ✅               |                  |
| `/flows/{flowId}/label`              | `HEAD`/`GET`    | ✅               | ✅              |                  |                  |
|                                      | `PUT`           | ✅               |                 | ✅               |                  |
|                                      | `DELETE`     ⚠️ | ✅               |                 | ✅               |                  |
| `/flows/{flowId}/read_only`          | `HEAD`/`GET`    | ✅               | ✅              |                  |                  |
|                                      | `PUT`           | ✅               |                 | ✅               |                  |
| `/flows/{flowId}/flow_collection`    | `HEAD`/`GET`    | ✅               | ✅              |                  |                  |
|                                      | `PUT`           | ✅               |                 | ✅               |                  |
|                                      | `DELETE`     ⚠️ | ✅               |                 | ✅               |                  |
| `/flows/{flowId}/max_bit_rate`       | `HEAD`/`GET`    | ✅               | ✅              |                  |                  |
|                                      | `PUT`           | ✅               |                 | ✅               |                  |
|                                      | `DELETE`     ⚠️ | ✅               |                 | ✅               |                  |
| `/flows/{flowId}/avg_bit_rate`       | `HEAD`/`GET`    | ✅               | ✅              |                  |                  |
|                                      | `PUT`           | ✅               |                 | ✅               |                  |
|                                      | `DELETE`     ⚠️ | ✅               |                 | ✅               |                  |
| `/flows/{flowId}/segments`           | `HEAD`/`GET`    | ✅               | ✅              |                  |                  |
|                                      | `POST`          | ✅               |                 | ✅               |                  |
|                                      | `DELETE`        | ✅               |                 |                  | ✅               |
| `/flows/{flowId}/storage`            | `POST`          | ✅               |                 | ✅               |                  |
| `/objects/{objectId}`                | `HEAD`/`GET`    | ✅               | ✅              |                  |                  |
| `/objects/{objectId}/instances`      | `POST`          | ✅               |                 | ✅               |                  |
|                                      | `DELETE`        | ✅               |                 | ✅               |                  |
| `/flow-delete-requests`              | `HEAD`/`GET` ⚠️ | ✅               |                 |                  |                  |
| `/flow-delete-requests/{request-id}` | `HEAD`/`GET` ⚠️ | ✅               |                 |                  | ✅               |

Key for the listing:

- ✅: Allow method with this OAuth scope
- ⚠️: Method does not follow the basic mapping of `tams-api/read` to `HEAD`/`GET`, `tams-api/write` to `POST`/`PUT`, and `tams-api/delete` to `DELETE`

Users may be assigned combinations of these roles for different purposes, for example:

- `administrator`: Has all four scopes
- `viewer`: Has `tams-api/read`
- `editor`: Has `tams-api/read` and `tams-api/write`
- `store-writer`: Has `tams-api/write`
- `store-cleanup-system`: Has `tams-api/delete`

To implement the authorisation, the authorisation server checks the requested scopes against the user's access when issuing a token.
The TAMS server, or its auth proxy, rejects requests without appropriate scopes.

## Finer Grained Authorisation

A further build on the very coarse role-based approach above is to expand the set of permissions to apply to specific Sources and Flows.
However the implementation of this can become complex and unwieldy, especially if each Source and Flow in the system has a separate set of permissions to manage and it becomes necessary to edit them all to implement a policy change.

Attribute-Based Access Control (ABAC) is one approach to manage this complexity, by describing permissions policies based on the attributes of resources (Sources and Flows), and if necessary, users as well.
However full ABAC can be challenging to implement and requires a degree of organisational maturity to construct and manage stable attributes.
This section describes a possible approach to ABAC authorisation logic to aid interoperability between TAMS implementations, in which content is assigned an attribute in the form of a "class".
This approach should be considered experimental at this point.
Due its experimental nature, this approach makes use of the tags feature in TAMS.
Future iterations of these proposals may elevate ABAC attributes to a specific field in the core specification.

### Scopes and Auth Classes

In practical TAMS solutions, ABAC could look like defining an `auth_classes` tag.
A permissions system then defines policies that evaluates permissions based on to those `auth_classes` and a request's claimed OAuth scopes.

For example, consider a service instance shared by multiple teams from the News and Sport production teams of an organisation.
Each team have the ability to read and write their own content, and no access to the other team's content.
However in some cases it is necessary to share a particular Source (e.g. to work on a shared story) to the other team.

| Resource       | Auth classes       | Comments                                            |
| -------------- | ------------------ | --------------------------------------------------- |
| Source Sport A | `sport`            | Sport have full access. News have no access.        |
| Source Sport B | `sport`            | Sport have full access. News have no access.        |
| Source News X  | `news`, `sport_ro` | News have full access. Sport have read access only. |
| Source News Y  | `news`             | News have full access. Sport have no access.        |

### Auth logic

In order that implementations may have consistent expectations about which methods they may access, this section provides recommended auth logic for methods.

It is assumed that admins have permission to execute all methods on all endpoints.
It is only explicitly called out in the listing below where admins are the only users granted permissions.

The listing below refers to requests having permissions, rather than users.
This is to account for cases where users only "claim" a subset of their permissions for a given request.
Note that in some circumstances, requests may have to claim more permissions than may initially be assumed.
For example - when editing the `auth_classes` tag on a Source/Flow/webhook, requests must claim both write permissions and the permission they are changing.
i.e. If the request adds or removes delete permissions for any group, it must have valid delete permissions itself.
This is to prevent permission escalation attacks such as a user with write permissions adding delete permissions to themselves.

Implementations may choose to additionally filter data based on the permissions of a request.
For example, where a Source collections may be filtered to only include Sources the request has read/write/delete permissions on.
Implementers should consider the implications of hiding data.
For example - hiding collection relationships may result in clients deciding to delete a resource which, unknowingly, is still referenced by another.

| Endpoint                             | Method       | Auth logic                                                                              |
| ------------------------------------ | ------------ | --------------------------------------------------------------------------------------- |
| `/`                                  | `HEAD`/`GET` | Available to all                                                                        |
| `/service`                           | `HEAD`/`GET` | Available to all                                                                        |
|                                      | `POST`       | Request must have admin permissions. Otherwise reject.                                  |
| `/service/storage-backends`          | `HEAD`/`GET` | Available to all                                                                        |
| `/service/webhooks`                  | `HEAD`/`GET` | Restrict returned data by adding list of claimed auth classes to `tag.auth_classes`. If the incoming request has `tag.auth_classes` set, the request must be processed with `tag.auth_classes` set to the intersection of the claimed auth classes and the provided list in `tag.auth_classes`. |
|                                      | `POST`       | If the request includes Source or Flow filters, the request must have read permissions on all Source or Flow IDs requested. Otherwise, reject. Note that this endpoint only allows creation, not modification, of webhooks. |
| `/service/webhooks/{webhookId}`      | `HEAD`/`GET` | Request must have read permissions on {webhookId}. Otherwise reject.                    |
|                                      | `PUT`        | Request must have write permissions on {webhookId}. If the request includes Source or Flow filters, the request must have read permissions on all Source or Flow IDs requested. If the request edits the `auth_classes` tag of a webhook, the request must have the permissions being edited. i.e. If the request adds or removes delete permissions for any group, it must have delete permissions on the webhook. Otherwise, reject. |
|                                      | `DELETE`     | Request must have delete permissions on {webhookId}. Otherwise, reject.                 |
| `/sources`                           | `HEAD`/`GET` | Restrict returned data by adding list of claimed auth classes to `tag.auth_classes`. If the incoming request has `tag.auth_classes` set, the request must be processed with `tag.auth_classes` set to the intersection of the claimed auth classes and the provided list in `tag.auth_classes`. |
| `/sources/{sourceId}`                | `HEAD`/`GET` | Request must have read permissions on {sourceId}. Otherwise reject.                     |
| `/sources/{sourceId}/tags`           | `HEAD`/`GET` | Request must have read permissions on {sourceId}. Otherwise reject.                     |
| `/sources/{sourceId}/tags/{name}`    | `HEAD`/`GET` | Request must have read permissions on {sourceId}. Otherwise reject.                     |
|                                      | `PUT`        | Request must have write permissions on {sourceId}. If the request is to `/sources/{sourceId}/tags/auth_classes` the request must have the permissions being edited. i.e. If the request adds or removes delete permissions for any group, it must have delete permissions on {sourceId}. Otherwise, reject. |
|                                      | `DELETE`     | Request must have write permissions on {sourceId}. If the request is to `/sources/{sourceId}/tags/auth_classes` the request must have the permissions being edited. i.e. If the request adds or removes delete permissions for any group, it must have delete permissions on {sourceId}. Otherwise, reject. |
| `/sources/{sourceId}/description`    | `HEAD`/`GET` | Request must have read permissions on {sourceId}. Otherwise reject.                     |
|                                      | `PUT`        | Request must have write permissions on {sourceId}. Otherwise, reject.                   |
|                                      | `DELETE`     | Request must have write permissions on {sourceId}. Otherwise, reject.                   |
| `/sources/{sourceId}/label`          | `HEAD`/`GET` | Request must have read permissions on {sourceId}. Otherwise reject.                     |
|                                      | `PUT`        | Request must have write permissions on {sourceId}. Otherwise, reject.                   |
|                                      | `DELETE`     | Request must have write permissions on {sourceId}. Otherwise, reject.                   |
| `/flows`                             | `HEAD`/`GET` | Restrict returned data by adding list of claimed auth classes to `tag.auth_classes`. If the incoming request has `tag.auth_classes` set, the request must be processed with `tag.auth_classes` set to the intersection of the claimed auth classes and the provided list in `tag.auth_classes`. |
| `/flows/{flowId}`                    | `HEAD`/`GET` | Request must have read permissions on {flowID}. Otherwise reject.                       |
|                                      | `PUT`        | If {flowId} does not currently exist, request must have write permissions on the Flow's Source ID if it already exists in this TAMS instance. If {flowId} already exists, request must have write permissions on {flowId}. If the request edits the `auth_classes` tag, the request must have the permissions being edited. i.e. If the request adds or removes delete permissions for any group, it must have delete permissions on {flowId}. Otherwise, reject. |
|                                      | `DELETE`     | Request must have delete permissions on {flowId}. Otherwise reject.                     |
| `/flows/{flowId}/tags`               | `HEAD`/`GET` | Request must have read permissions on {flowId}. Otherwise reject.                       |
| `/flows/{flowId}/tags/{name}`        | `HEAD`/`GET` | Request must have read permissions on {flowId}. Otherwise reject.                       |
|                                      | `PUT`        | Request must have write permissions on {flowId}. If the request is to `/flows/{flowId}/tags/auth_classes` the request must have the permissions being edited. i.e. If the request adds or removes delete permissions for any group, it must have delete permissions on {flowId}. Otherwise, reject. |
|                                      | `DELETE`     | Request must have write permissions on {flowId}. If the request is to `/flows/{flowId}/tags/auth_classes` the request must have the permissions being edited. i.e. If the request adds or removes delete permissions for any group, it must have delete permissions on {flowId}. Otherwise, reject. |
| `/flows/{flowId}/description`        | `HEAD`/`GET` | Request must have read permissions on {flowId}. Otherwise reject.                       |
|                                      | `PUT`        | Request must have write permissions on {flowId}. Otherwise reject.                      |
|                                      | `DELETE`     | Request must have write permissions on {flowId}. Otherwise reject.                      |
| `/flows/{flowId}/label`              | `HEAD`/`GET` | Request must have read permissions on {flowId}. Otherwise reject.                       |
|                                      | `PUT`        | Request must have write permissions on {flowId}. Otherwise reject.                      |
|                                      | `DELETE`     | Request must have write permissions on {flowId}. Otherwise reject.                      |
| `/flows/{flowId}/read_only`          | `HEAD`/`GET` | Request must have read permissions on {flowId}. Otherwise reject.                       |
|                                      | `PUT`        | Request must have write permissions on {flowId}. Otherwise reject.                      |
| `/flows/{flowId}/flow_collection`    | `HEAD`/`GET` | Request must have read permissions on {flowId}. Otherwise reject.                       |
|                                      | `PUT`        | Request must have write permissions on {flowId}. Otherwise reject.                      |
|                                      | `DELETE`     | Request must have write permissions on {flowId}. Otherwise reject.                      |
| `/flows/{flowId}/max_bit_rate`       | `HEAD`/`GET` | Request must have read permissions on {flowId}. Otherwise reject.                       |
|                                      | `PUT`        | Request must have write permissions on {flowId}. Otherwise reject.                      |
|                                      | `DELETE`     | Request must have write permissions on {flowId}. Otherwise reject.                      |
| `/flows/{flowId}/avg_bit_rate`       | `HEAD`/`GET` | Request must have read permissions on {flowId}. Otherwise reject.                       |
|                                      | `PUT`        | Request must have write permissions on {flowId}. Otherwise reject.                      |
|                                      | `DELETE`     | Request must have write permissions on {flowId}. Otherwise reject.                      |
| `/flows/{flowId}/segments`           | `HEAD`/`GET` | Request must have read permissions on {flowId}. Otherwise reject.                       |
|                                      | `POST`       | Request must have write permissions on {flowId}, and either this must be the first registration of the Media Object(s) (i.e. `/objects/{objectId}` returns 404) or the request must have read access to the Media Object(s) being written. Otherwise reject.    |
|                                      | `DELETE`     | Request must have write permissions on {flowId}. Otherwise reject.                      |
| `/flows/{flowId}/storage`            | `POST`       | Request must have write permissions on {flowId}. Otherwise reject.                      |
| `/objects/{objectId}`                | `HEAD`/`GET` | Restrict returned data in `referenced_by_flows` property by adding list of claimed auth classes to `flow_tag.auth_classes`. If the incoming request has `flow_tag.auth_classes` set, the request must be processed with `flow_tag.auth_classes` set to the intersection of the claimed auth classes and the provided list in `flow_tag.auth_classes`. |
| `/objects/{objectId}/instances`      | `POST`       | Request must have write permissions on {objectId}. Otherwise reject.                    |
|                                      | `DELETE`     | Request must have write permissions on {objectId}. Otherwise reject.                    |
| `/flow-delete-requests`              | `HEAD`/`GET` | Request must have admin permissions. Otherwise reject.                                  |
| `/flow-delete-requests/{request-id}` | `HEAD`/`GET` | Request must have delete permissions on the Delete Request's Flow ID. Otherwise reject. |

### Determining base permissions

#### Flows

Read, write, and delete permissions on individual Flows may be determined via auth classes listed in the `auth_classes` tag on the Flow.
This may be done via the `/flows/{flowId}/tags/auth_classes` endpoint.

#### Sources

Read, write, and delete permissions on individual Sources may be determined via auth classes listed in the `auth_classes` tag on the Source.
This may be done via the `/sources/{sourceId}/tags/auth_classes` endpoint.

#### Media Objects

Read, write, and delete permissions on individual Media Objects may be determined by filtering returned Flows on the Media Object.
This may be done by setting `flow_tag.auth_classes` to relevant claimed auth classes (e.g. auth classes with read permissions if read permissions on the Media Object are to be verified).
If `referenced_by_flows` in the returned data is empty, the request DOES NOT have the relevant permissions.
If `referenced_by_flows` in the returned data is not empty, the request DOES have the relevant permissions.

#### Webhooks

Read, write, and delete permissions on webhooks may be determined via auth classes listed in the `auth_classes` tag on webhooks.
The webhooks endpoint may be filtered to those with specific auth classes using the `tag.auth_closses` query parameter.

### Handling rejected requests

Where requests are rejected, they should return as follows:

- `404` if the request has no permissions on the endpoint
- `403` if the request has any permission on the endpoint, but not sufficient to complete the request

### Fine-grained authorisation and webhook events

Implementations must evaluate permissions against webhook events themselves as well as the API's HTTP endpoints.
A basic implementation may enumerate Flows and Sources a user has access to when creating/updating the webhook and use this to filter events.
This approach is strongly discouraged as permissions may change over time.
It is recommended that implementations assess permissions on a per-event basis.
Implementations may use `auth_classes` tags in Flow/Source updated events to maintain a cache of Flow/Sources a webhook has read permissions for.
Implementations should regularly inspect Source/Flow tags, via the HTTP API or other methods, to guard against missed events.
Implementations should regularly check the user's permissions in the auth system for changes.
If permissions changes are observed, the set of permissions used to evaluate against events should only ever be reduced in scope and never increased.

### Adding Flows to Sources

New Sources inherit permissions from the first Flow which references them.
In order to prevent malicious actors adding maliciously crafted Flows to an existing Source, Flows using an existing Source ID SHOULD have write write permissions on the Source.
This may be an impediment to some workflows, such as where dual-redundant ingesters capture the same Source.
Or where different teams within a business re-ingest the same Source in a different format.
Some deployments may choose to accept this risk and allow broader re-use of Sources.
Implementations may either apply default auth classes to Sources which will grant all users write permissions, or they may use more permissive auth logic.

### Implementation

To implement the model above, a way to hold the auth classes in TAMS is needed, along with a system to store the permissions and the authorisation logic that maps them to auth classes.

For the latter, [Amazon Verified Permissions](https://aws.amazon.com/verified-permissions/) and [Permify](https://github.com/Permify/permify) may both serve as permissions management tools.
They allow authorisation decisions to be made by taking a set of policies defined in some domain-specific language, along with the attributes of the user (group membership) and resource (Source/Flow/webhook auth classes), and computing whether to allow the request.
They may also return the permitted resource attributes (Source/Flow/webhook auth classes) for a given user of a given endpoint.
This may be useful when filtering results in Flow listings, for example.
This decision process is intended to be run inline for each request, for example at an authenticating proxy placed in front of the API server.

For storing auth classes an initial proof-of-concept could be built using Source, Flow, and webhook tags as described above.
A "special" `auth_classes` tag would store a comma-separated list of auth classes assigned to a Flow, Source or webhook.
The authenticating proxy would need to take steps to prevent unauthorised modification of this special tag, as described above.

As a result, the process of authorising a request is:

1. Read the list of auth classes assigned to the resource
2. Read the user's claimed scopes from their provided token
3. Request a decision from the permissions system based on those data
4. (Write requests only): Check whether the request would modify the special `auth_classes` tag, and confirm the user has permission to make that modification
5. (Flow Segment write requests only): Check if the Media Object already exists in the service instance using the `/objects` endpoint, and if it does, confirm the user would have access to read it
6. (Write requests only): Propagate any changes to the `auth_classes` tag to Flows and Sources collected by this one

## Where to Enforce Authorisation

Some consideration should be given for where to apply the authorisation step, depending on how TAMS is deployed and integrated.
For example a TAMS instance could be deployed with fine-grained authorisation support, and used directly by systems across an organisation.
In this case it would make sense to treat all clients of that TAMS instance as identical from an authentication/authorisation perspective: for example a user operating an NLE would be expected to provide suitable authorised credentials, but so too would the organisations MAM when it wants access to the service instance.

Another deployment approach might see a MAM or other tool expose a TAMS API interface itself, which is proxied through to some simpler backing store.
In this case the MAM might manage and enforce other policies and rules around access to content, so it would make more sense to do the same in the TAMS API interface, and then use the MAM's own credentials to access the backing TAMS instance.

## Use cases and additional optional functionality

### Providing access to a subset of a Flow's timerange

The model described above allows access control at the Source/Flow level.
Some use cases may require finer grained control.
This may be achieved by creating a new Flow with the relevant permissions that refers to the Objects of interest.
Caution should be taken where the boundary timestamps land partway through an Object.
Where the material around the boundaries is sensitive, new trimmed Objects should be created at the boundaries that remove content outside the permitted range.

### Global read access

Some organisations/implementations may choose to provide read access to all Sources and Flows to promote content re-use, and reduce the writing of duplicate content to the service instance.
Implementations may provide this feature by either adding default groups to Sources and Flows that provide appropriate read access to users, or by using more permissive auth logic.

### Permissions propagation

The basic implementation described above will populate auth classes on a new Source with those in the Flow that results in its creation.
This is a product of TAMS' general behaviour of populating Source metadata from Flows on creation.

Some implementations may also find it useful to propagate changes of Source permissions to their Flows, and Source/Flow permissions down to Sources and Flows they collect.
For example, where Multi Source A collects Video Source B and Audio Source C, changes to permissions on Source A would be reflected on Sources B and C as well as the Flows of A, B, and C.
The propagation of these permissions should happen on write to avoid the need for potentially extensive tree traversal on read.
When changes are propagated, they must only be applied to resources where the request has the permission to edit auth classes.
Where propagation reaches a resource that the request doesn't have sufficient permissions to edit, the process will stop following that branch of the resource tree.
Propagation of permissions should only be performed after the successful modification of a parent resource.

Propagation should also be triggered when a new Source/Flow is added to a Source/Flow collection, or when a Flow is added to an existing Source.

### Deny permissions

Implementations may wish to support auth classes and related auth logic that explicitly denies permissions against resources.
In these cases, a matching "deny" class takes precedent over an "allow" class.

## Future Work

The model described above allows for more use cases than coarse-grained RBAC: especially use cases where multiple tenants share a single service instance.
However it would be useful to allow more attributes to be used in rules: for example allowing write access to the tags of Sources/Flows but not other properties.

One of the areas noted in [ADR0028: Authentication Methods](../adr/0028-authentication-methods.md) is being able to issue credentials restricted to a limited subset of Sources or Flows, which must also be supported by the authorisation system.
This could be achieved by issuing JWT bearer tokens using the [RFC9396 authorization details](https://www.rfc-editor.org/rfc/rfc9396.html#name-authorization-request) field to embed permissions granted directly into the token.
It would also allow for a suitable authenticating proxy to validate access without making a query to the authorisation server or permissions system, instead relying on the access claimed in the token, along with the cryptographic properties of the token itself.
