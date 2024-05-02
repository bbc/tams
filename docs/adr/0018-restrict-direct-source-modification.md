---
status: "accepted"
---
# Restrict direct Source modification

## Context and Problem Statement

This ADR modifies [ADR 0002](./0002-add-sources-to-api.md) to remove direct Create, Update, and Delete operations.

There are currently inconsistencies in the mechanisms to create/update Source's in the TAMS API.
Sources are implicitly created when creating a Flow that references them.
Source endpoints have a `PUT` operation which may also be used to create Sources without any associated Flows.
The `PUT` operation may be used to modify some, but not all, properties on the Source.
There are some properties which we do not wish clients to modify (e.g. `format`, `modified-by`).
Those properties are ignored if included in a `PUT` request for an existing Source.
This behaviour is not ideal RESTful behaviour.

Some, but not all, of the modifiable properties may also be modified specific endpoints.
The exception is the Source `label` which may only be modified by a `PUT` request on the Source endpoint.

Source endpoints do not support `DELETE` requests.
But when all Flows associated with a Source are deleted, the Source will also be deleted implicitly.

The ability to create Source's directly was added following [ADR 0002](./0002-add-sources-to-api.md), in part to allow pre-empt the addition of basic Source <-> Source relationship representations.
The implementation of Source <-> Source relationships was added in [ADR 0012](./0012-add-flow-collections.md).
The proposal, however, is that relationships should be created at the Flow level, i.e. Flow <-> Flow, and the Source <-> Source relationship be inferred from this.
The process of creating a Source with Collects others would therefore be to create a Flow that collects other Flows and have the Source, and Source <-> Source relationships created implicitly.
Even if that Flow that collects has no stored segments.
This was chosen as Flow <-> Flow relationships cannot be completely inferred from the data available in Source <-> Source relationships, but the reverse is possible.
This removes the only known use case for direct creation of Sources.

## Decision Drivers

* Make endpoints for modifying Sources consistent
* Make modification of Sources more RESTful in behaviour
* Provide consistent workflows/behaviours for creating/deleting Sources

## Considered Options

* Option A1: Retain current Source creation `PUT` behaviour
* Option A2: Remove ability to create Sources via `PUT` requests on sources endpoint
* Option B1: Retain current Source modification `PUT` behaviour
* Option B2: Remove ability to modify Sources via `PUT` requests on sources endpoint
* Option C1: Do not add additional endpoints for managing Source metadata
* Option C2: Add additional endpoints for managing Source metadata
* Option D1: Add the ability to use `DELETE` requests on sources endpoints
* Option D2: Do not add `DELETE` requests on sources endpoint

## Decision Outcome

Chosen option: A2, B2, C2, and D2, because this combination will provide a consistent RESTful interface.
This combination best matches current expected usage patterns.
And it makes expected behaviour around creation/deletion of Sources, and modification of metadata more clear.

## Pros and Cons of the Options

### Option A1: Retain current Source creation `PUT` behaviour

* Good, because it supports the use of Sources with no associated Flows, which are possible in the data model
* Neutral, because we do not foresee real-world use cases for Sources without Flows in TAMS
* Bad, because it results in multiple possible routes to creating a Source (explicit Source creation, or implied via Flow creation)
  * This could lead to race conditions in Source creation, and inconsistent approaches to common tasks

### Option A2: Remove ability to create Sources via `PUT` requests on sources endpoint

* Good, because it results in one possible route to creation of Sources
* Neutral, because it removes support for a theoretical capability of the data model for which we don't have use cases

### Option B1: Retain current Source modification `PUT` behaviour

* Good, because it allows for the modification of all Source metadata in a single request
* Bad, because it isn't immediately clear which metadata items may be modified in the request
* Bad, because ignoring some parts of the request body isn't best practice in a RESTful API

### Option B2: Remove ability to modify Sources via `PUT` requests on sources endpoint

* Good, because it brings the API in line with best practice for RESTful interfaces
* Neutral, because it will require the choice of Option C2, instead of Option C1
* Neutral, because updating multiple pieces of metadata will require multiple requests

### Option C1: Do not add additional endpoints for managing Source metadata

* Bad, because it maintains an inconsistency in endpoints for managing Source metadata

### Option C2: Add additional endpoints for managing Source metadata

* Good, because it improves consistency in endpoints for managing Source metadata

### Option D1: Add the ability to use `DELETE` requests on sources endpoints

* Good, because if Option A1 and/or B1 are chosen, it would provide full CRUD operation support on the Sources endpoints
* Bad, because it would add complexity in:
  * How to handle Sources when all associated Flows are deleted
  * How to handle existing Flows if associated Sources are deleted
* Bad, because it would possibly add an additional means to delete Sources alongside the current implied delete when all associated Flows are deleted

### Option D2: Do not add `DELETE` requests on sources endpoint

* Good, because it results in one possible route to the deletion of Sources (implied, once all related Flows are deleted)
* Neutral, because if Options A2 and B2 are chosen, the Sources endpoints become consistently read-only

## More Information

Outcome of discussion involving James Sandford, Sam Mesterton-Gibbons, Robert Wadge, Mark Himsley, and John Biltcliffe.

It is possible that we will want to expand out on this functionality in future. As things stand, this proposal brings consistency to the API ahead of the v4.0 release which will be used by Cloud-Native Agile Production (CNAP) partners for initial integration. A minor revision in future to add functionality is considered less disruptive than a major revision to remove/otherwise break functionality.