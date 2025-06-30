# 0016: Authorisation in TAMS Workflows

## Abstract

Media workflows often contain sensitive or high-value content, and media organisations need to effectively manage access to that content across their estate.
That requires suitable approaches across both authentication (identifying the user) as discussed in [ADR0028](../adr/0028-authentication-methods.md), and also authorisation (deciding what the user can do), which is discussed here.
In general, store implementations, and the organisations that deploy them, are free to define how the authorisation model works based on their needs, however this Application Note provides some guidelines and a starting point.

## Overall Principles

Implementers should consider the material they need to protect, the nature of their business and their threat model when deciding how to build authorisation into TAMS-based media workflows.

For some organisations a coarse-grained approach is sufficient: for example allowing groups of users to have read- or write-access to a store or large blocks of content.
This might be appropriate for example in a newsroom, where staff are deliberately enabled to work together and access each other's material.

Conversely a finer-grained approach may be required, where specific rules and policies are applied to each piece of content, and groups of users are carefully managed.
This may be appropriate for example when working with a large number of third parties and freelancers in drama production, or when managing a large media archive of high-value content.

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
|                                      | `POST`       ⚠️ | ✅               | ❌              | ❌               | ❌               |
| `/service/storage-backends`          | `HEAD`/`GET` ⚠️ | ❌               | ✅              | ✅               | ❌               |
| `/service/webhooks`                  | `HEAD`/`GET` ⚠️ | ✅               | ❌              | ❌               | ❌               |
|                                      | `POST`       ⚠️ | ✅               | ❌              | ❌               | ❌               |
| `/sources`                           | `HEAD`/`GET`    | ❌               | ✅              | ❌               | ❌               |
| `/sources/{sourceId}`                | `HEAD`/`GET`    | ❌               | ✅              | ❌               | ❌               |
| `/sources/{sourceId}/tags`           | `HEAD`/`GET`    | ❌               | ✅              | ❌               | ❌               |
| `/sources/{sourceId}/tags/{name}`    | `HEAD`/`GET`    | ❌               | ✅              | ❌               | ❌               |
|                                      | `PUT`           | ❌               | ❌              | ✅               | ❌               |
|                                      | `DELETE`     ⚠️ | ❌               | ❌              | ✅               | ❌               |
| `/sources/{sourceId}/description`    | `HEAD`/`GET`    | ❌               | ✅              | ❌               | ❌               |
|                                      | `PUT`           | ❌               | ❌              | ✅               | ❌               |
|                                      | `DELETE`     ⚠️ | ❌               | ❌              | ✅               | ❌               |
| `/sources/{sourceId}/label`          | `HEAD`/`GET`    | ❌               | ✅              | ❌               | ❌               |
|                                      | `PUT`           | ❌               | ❌              | ✅               | ❌               |
|                                      | `DELETE`     ⚠️ | ❌               | ❌              | ✅               | ❌               |
| `/flows`                             | `HEAD`/`GET`    | ❌               | ✅              | ❌               | ❌               |
| `/flows/{flowId}`                    | `HEAD`/`GET`    | ❌               | ✅              | ❌               | ❌               |
|                                      | `PUT`           | ❌               | ❌              | ✅               | ❌               |
|                                      | `DELETE`        | ❌               | ❌              | ❌               | ✅               |
| `/flows/{flowId}/tags`               | `HEAD`/`GET`    | ❌               | ✅              | ❌               | ❌               |
| `/flows/{flowId}/tags/{name}`        | `HEAD`/`GET`    | ❌               | ✅              | ❌               | ❌               |
|                                      | `PUT`           | ❌               | ❌              | ✅               | ❌               |
|                                      | `DELETE`     ⚠️ | ❌               | ❌              | ✅               | ❌               |
| `/flows/{flowId}/description`        | `HEAD`/`GET`    | ❌               | ✅              | ❌               | ❌               |
|                                      | `PUT`           | ❌               | ❌              | ✅               | ❌               |
|                                      | `DELETE`     ⚠️ | ❌               | ❌              | ✅               | ❌               |
| `/flows/{flowId}/label`              | `HEAD`/`GET`    | ❌               | ✅              | ❌               | ❌               |
|                                      | `PUT`           | ❌               | ❌              | ✅               | ❌               |
|                                      | `DELETE`     ⚠️ | ❌               | ❌              | ✅               | ❌               |
| `/flows/{flowId}/read_only`          | `HEAD`/`GET`    | ❌               | ✅              | ❌               | ❌               |
|                                      | `PUT`           | ❌               | ❌              | ✅               | ❌               |
| `/flows/{flowId}/flow_collection`    | `HEAD`/`GET`    | ❌               | ✅              | ❌               | ❌               |
|                                      | `PUT`           | ❌               | ❌              | ✅               | ❌               |
|                                      | `DELETE`     ⚠️ | ❌               | ❌              | ✅               | ❌               |
| `/flows/{flowId}/max_bit_rate`       | `HEAD`/`GET`    | ❌               | ✅              | ❌               | ❌               |
|                                      | `PUT`           | ❌               | ❌              | ✅               | ❌               |
|                                      | `DELETE`     ⚠️ | ❌               | ❌              | ✅               | ❌               |
| `/flows/{flowId}/avg_bit_rate`       | `HEAD`/`GET`    | ❌               | ✅              | ❌               | ❌               |
|                                      | `PUT`           | ❌               | ❌              | ✅               | ❌               |
|                                      | `DELETE`     ⚠️ | ❌               | ❌              | ✅               | ❌               |
| `/flows/{flowId}/segments`           | `HEAD`/`GET`    | ❌               | ✅              | ❌               | ❌               |
|                                      | `POST`          | ❌               | ❌              | ✅               | ❌               |
|                                      | `DELETE`        | ❌               | ❌              | ❌               | ✅               |
| `/flows/{flowId}/storage`            | `POST`          | ❌               | ❌              | ✅               | ❌               |
| `/objects/{objectId}`                | `HEAD`/`GET`    | ❌               | ✅              | ❌               | ❌               |
| `/flow-delete-requests`              | `HEAD`/`GET` ⚠️ | ✅               | ❌              | ❌               | ❌               |
| `/flow-delete-requests/{request-id}` | `HEAD`/`GET` ⚠️ | ❌               | ❌              | ❌               | ✅               |

Key for the listing:

- ✅: Allow method with this OAuth scope
- ❌: Do not allow method with this OAuth scope.
Other claimed scopes may still allow this method
- ⚠️: Method does not follow the basic mapping of `tams-api/read` to `HEAD`/`GET`, `tams-api/write` to `POST`/`PUT`, and `tams-api/delete` to `DELETE`

Users may be assigned combinations of these roles for different purposes, for example:

- `administrator`: Has all four scopes
- `viewer`: Has `tams-api/read`
- `editor`: Has `tams-api/read` and `tams-api/write`
- `store-writer`: Has `tams-api/write`
- `store-cleanup-system`: Has `tams-api/delete`

To implement the authorisation, the authorisation server checks the requested scopes against the user's access when issuing a token.
The TAMS server, or it's auth proxy, rejects requests without appropriate scopes.

## Finer Grained Authorisation

A further build on the very coarse role-based approach above is to expand the set of permissions to apply to specific Sources and Flows.
However the implementation of this can become complex and unwieldy, especially if each Source and Flow in the system has a separate set of permissions to manage and it becomes necessary to edit them all to implement a policy change.

Attribute-based Access Control (ABAC) is one approach to manage this complexity, by describing permissions policies based on the attributes of resources (Sources and Flows), and if necessary, users as well.
However full ABAC can be challenging to implement and requires a degree of organisational maturity to construct and manage stable attributes.
This topic is well outside the scope of this document, however there exists plenty of literature and tools implementing ABAC in general terms.

In practical TAMS solutions, this could look like defining a "class" attribute which can be applied to a Source or Flow, where "class" could also be thought of as "owner" or "project".
A permissions system then defines policies that apply to those classes.

For example, consider a store shared by multiple teams from the News and Sport production teams of an organisation.
Each team have the ability to read and write their own content, and no access to the other team's content.
However in some cases it is necessary to share a particular Source (e.g. to work on a shared story) to the other team.

| Resource       | Classes | Comments |
| -------------- | ------- | -------- |
| Source Sport A | sport | |
| Source Sport B | sport | |
| Source News X  | news, sport_share | This item is shared across to Sport |
| Source News Y  | news | |

The permissions policies are then implemented as:

- Users in the "sport" user group have read and write access to all content in the "sport" class
- Users in the "news" user group have read and write access to all content in the "news" class
- Users in the "sport" user group have read access to all content in the "sport_share" class

### Implementation

To implement the model above, way to hold the classes in the store is needed, along with a system to store the permissions and how they map on to classes.

For the latter, [Amazon Verified Permissions](https://aws.amazon.com/verified-permissions/) and [Permify](https://github.com/Permify/permify) both serve as permissions management tools.
They allow authorisation decisions to be made by taking a set of policies defined in some domain-specific language, along with the attributes of the user (group membership) and resource (Source/Flow class), and computing whether to allow the request.
This decision process is intended to be run inline for each request, for example at an authenticating proxy placed in front of the API server.

For storing classes, an initial proof-of-concept could be built using Source and Flow tags: for example defining "special" tags such as `authz_class.news = 1` (using one tag per class to enable querying for presence of that tag, which is not possible with e.g. a comma-separated list).
The authenticating proxy would need to take steps to prevent unauthorised modification of this special tag.

In addition, it should be possible to set a class on a multi-essence Source or Flow, and apply that permissions downwards to all the Sources or Flows it collects.
Similarly, classes should be set by default on a Source (and apply to all Flows), but be settable on individual Flows as well for additional flexibility.
To avoid a complex traversal of potentially a large hierarchy (and to simplify the listing endpoints), it may be useful to denormalise the tag on write, writing it to all the Sources and Flows it would affect as well.

As a result, the process of authorising a request is:

1. Read the list of classes assigned to the resource
2. Read the user's groups from their provided token
3. Request a decision from the permissions system based on those data
4. (Write requests only): Check whether the request would modify a special `authz_*` tag, and confirm the user has permission to make that modification
5. (Flow segment write requests only): Check if the object already exists in the store using the `/objects` endpoint, and if it does, confirm the user would have access to read it
6. (Write requests only): Propagate any changes to `authz_class` tags to Flows and Sources collected by this one

## Where to Enforce Authorisation

Some consideration should be given for where to apply the authorisation step, depending on how TAMS is deployed and integrated.
For example a TAMS instance could be deployed with fine-grained authorisation support, and used directly by systems across an organisation.
In this case it would make sense to treat all clients of that TAMS instance as identical from an authentication/authorisation perspective: for example a user operating an NLE would be expected to provide suitable authorised credentials, but so too would the organisations MAM when it wants access to the store.

Another deployment approach might see a MAM or other tool expose a TAMS API interface itself, which is proxied through to some simpler backing store.
In this case the MAM might manage and enforce the other policies and rules around access to content, so it would make more sense to do the same in the TAMS API interface, and then use the MAM's own credentials to access the backing TAMS instance.

## Future Work

The model described above allows for more use cases than coarse-grained RBAC: especially use cases where multiple tenants share a single store.
However it would be useful to allow more attributes to be used in rules: for example making the tags of the Sources/Flows available to write policies upon as well.

Furthermore the finer-grained model makes listing Sources and Flows difficult: items in the list from the backing database that the user does not have access to should be removed.
For a small number of policies, this may be achievable by appending `?tag=<XXXX>` queries in the authenticating proxy (and then merging the results if multiple classes are involved).
However for a larger and more complex system, it may be necessary to integrate policies into the TAMS implementation itself, using queries to the underlying database to limit results based on policies.

One of the areas noted in [ADR0028: Authentication Methods](../adr/0028-authentication-methods.md) is being able to issue credentials restricted to a limited subset of Sources or Flows, which must also be supported by the authorisation system.
This could be achieved by issuing JWT bearer tokens using the [RFC9396 authorization details](https://www.rfc-editor.org/rfc/rfc9396.html#name-authorization-request) field to embed permissions granted directly into the token.
It would also allow for a suitable authenticating proxy to validate access without making a query to the authorisation server or permissions system, instead relying on the access claimed in the token, along with the cryptographic properties of the token itself.
