---
status: proposed
---
# Roles in Collections

## Context and Problem Statement

Each item in the collection of a multi-essence Source or Flow has a `role`, intended as a description of that item's purpose in the collection.
Roles are intended to be human-readable, and some conventions have developed around how they get used and their values.
However the role value is frequently used to express the editorial purpose of an item as free text, and to locate the item of interest in a collection.
Some better recommendations would be useful around how these cases should be handled, and what values used.

## Decision Drivers

* Roles must be set when creating a multi-essence collection.
* Most of the role values used or proposed are properties of the underlying Source/Flow, not its position in the collection
* When viewing a multi-essence Source or Flow, only the list of IDs collected and roles are available: getting formats and tags requires another query.
* As a result `role` is often used to capture that one Flow is `video` and another `audio`, but practical applications need to represent more complex packages.
* Items in a collection serve a variety of different purposes, and it is useful to have some commonality.
* Common selection and display conventions are useful as content is read from TAMS across multiple clients and services.

## Considered Options

* Option 1: Make `role` a semi-structured field containing editorial purpose, media type and other details
* Option 2: Replace `role` with additional controlled fields
* Option 3: Use `role` as editorial purpose, use other queries for Flow/Source properties
* Option 4a: Capture editorial purpose elsewhere, use `role` as an optional label
* Option 4b: Capture editorial purpose elsehwere, use `role` as an optional label, add a `priority` for sorting

## Decision Outcome

Chosen option: Option 4b because it avoids storing properties of Flows and Sources on collection items, instead keeping them on the objects they naturally fit with.
It also limits the changes required to the API, and while in some cases it may trigger extra API requests (e.g. to get the details of items in a collection), it is likely the details of those collection items will be needed anyway, so the requests would be needed, and was made less onerous by the additional query parameters introduced in [ADR0049](./0049-source-collected_by-query-parameter.md) (<https://github.com/bbc/tams/pull/183>).
Furthermore the TAMS API is intended not to serve as a Media Asset Manager and provide minimal library management and discovery features: through that lens the additional request burden seems reasonable and if it becomes too onerous in a particular deployment, that may indicate a MAM is required.

One aspect that came up during consideration of `role` was how to map and represent different audio channels, which will be fully explored in a future ADR.

### Implementation

Implemented by <https://github.com/bbc/tams/pull/173>

## Pros and Cons of the Options

### Option 1: Make `role` a semi-structured field containing editorial purpose, media type and other details

Write an Application Note suggesting a naming convention for the `role` field, with a structured form that captures media type, editorial purpose and additional details.
This would be similar to the approach taken in the (now deprecated) [storage label AppNote](../appnotes/0009-storage-label-format.md).
Clients could either read the collection items and identify both type and purpose, or query the members of the collection and consider their labels/tags directly instead.

* Good, because it avoids a breaking change to the specification, instead only creating guidance.
* Good, because it makes `role` open-ended, allowing space for future change and expansion.
* Good, because it provides a direct path to identifying the collection member of interest.
* Good, because it saves making additional API requests to get media type and other details of collection items.
* Bad, because it does not constrain the use of `role`, and clients may have to rely on human intervention.
* Bad, because it forces clients to handle and parse an un-enforced free-text field, which may be malformed as a result.
* Bad, because it duplicates information (media type, purpose, etc.) into the `role` field of each collected item.

### Option 2: Replace `role` with additional controlled fields

Change the specification to remove `role` and replace it with a more precise set of fields conveying the purpose of each element in the collection.
Some of these fields might actually be set on Flows or Sources and then the entry in the collection becomes a view into that canonical data.
For example `editorial_purpose`, `format` and `codec` fields might be surfaced.

* Good, because it constrains and precisely describes what each item in a collection is for.
* Good, because it provides a direct path to identifying the collection member of interest.
* Bad, because it requires a breaking change to the API, to provide a capability that can be achieved another way.
* Bad, because the required list of fields is not clear and requires more exploration.
* Bad, because it presents properties of Flows and Sources as properties of their position in the collection.

### Option 3: Use `role` as editorial purpose, use other queries for Flow/Source properties

Use `role` primarily as a label to represent the editorial purpose of an item in a collection (broadly aligned with common usage).
Where a client needs to know more about a collection item (for example whether it is video or audio) they can request the full details from the API.
For example if a collection contains multiple items of role "programme" the client could request all of those items by ID to find out one was video and one audio (or, subject to a draft ADR being accepted, make a direct query of `GET /flows?collected_by_id=...` and cross-reference the results with the collection listing).

* Good, because it aligns with current common usage of `role`.
* Good, because it avoids a breaking change to the specification.
* Bad, because it forces clients to make additional requests (and possibly a somewhat complex cross-reference) to locate all the data they need.
  In particular a UI element displaying all the Sources in a store, the editorial purposes they contain and their media types would require an additional listing request per top-level Source.
* Bad, because it presents properties of Flows and Sources as properties of their position in the collection.

### Option 4a: Capture editorial purpose elsewhere, use `role` as an optional label

Add an additional field or tag to capture editorial purpose instead of the somewhat arbitrary `role` (precise details are covered in [ADR0053](./0053-editorial-purpose-tag.md)).
Make `role` an optional field, intended solely to aid with human readability and rendering.
Require clients to make Source/Flow listing requests for Sources/Flows collected by a given ID to find full details.

* Good, because it keeps properties of the Source/Flow on that object, instead of in the collection.
* Good, because it simplifies client implementations that need not worry about the "correct" value of `role`.
* Good, because it avoids a breaking change to the specification.
* Bad, because it forces clients to make additional requests to locate all the data they need.
* Bad, because it removes the UI cue for how collections should be rendered and explored

### Option 4b: Capture editorial purpose elsewhere, use `role` as an optional label, add a `priority` for sorting

As Option 4a, except add an additional `priority` field defining a sort order for collection items when displayed (e.g. in a UI) and for selecting defaults.
Lower priorities sort first, with the order of equivalent values being undefined.
Not being set causes sorting last.

* Good, because it keeps properties of the Source/Flow on that object, instead of in the collection.
* Good, because it simplifies client implementations that need not worry about the "correct" value of `role`.
* Good, because it avoids a breaking change to the specification.
* Good, because it provides an optional stable ordering and default-selection behaviour in UIs and players.
* Bad, because it forces clients to make additional requests to locate all the data they need.
