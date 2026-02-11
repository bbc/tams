---
status: proposed
---
# Role Naming Convention

## Context and Problem Statement

Each item in the collection of a multi-essence Source or Flow has a `role`, intended as a description of that item's purpose in the collection.
Roles are intended to be human-readable, however it is useful for clients and systems to make sense of them too.
It would be useful to have some recommendations about how to use roles.

One part of that recommendation should be the editorial purpose of an item: for example programme audio, audio description or commentary.
Or main video, signed video or clean-feed without graphics.
Currently this is represented in free text.

## Decision Drivers

* Roles must be set when creating a multi-essence collection.
* When viewing a multi-essence Source or Flow, only the list of IDs collected and roles are available: getting formats and tags requires another query.
* Items in a collection serve a variety of different purposes, and it is useful to have some commonality.
* At time of writing `role` is typically `video` or `audio`, but practical applications need to represent more complex packages.

## Considered Options

For how to use the `role` field (options `Rn`):

* Option R1: Make `role` a semi-structured field containing editorial purpose, media type and other details
* Option R2: Replace `role` with a number of additional controlled fields
* Option R3a: Use `role` as editorial purpose, use other queries for Flow/Source properties
* Option R3b: Use `role` as editorial purpose, use other queries for Flow/Source properties, surface `role` as a query param
* Option R3c: Use `role` as editorial purpose, additionally surface `format` in collection

For how to represent editorial purpose (options `Pn`):

* Option P1: Represent editorial purpose using DVB component descriptors
* Option P2: Represent editorial purpose using roles from MPEG-DASH
* Option P3: Represent editorial purpose based on descriptions in the MovieLabs Ontology for Media Creation
* Option P4: Represent purpose of content using a list, as with tags

## Decision Outcome

Chosen option: Option 1a and Option 2d, because this allows `role` to be free-form and evolve over time, and avoids a breaking change to the specification or unduly constraining it.
While this prevents clients from being able to automatically determine the purpose of each item in a collection, in many cases the role merely serves to change what the user is shown and they are left to make the decisions.
In cases where it matters which elements of a collection are picked up (for example packaging content for distribution) the correct items should be identified by some more rigorous method anyway (for example creating a multi-essence Flow of just the items required).

### Implementation

Implemented by <https://github.com/bbc/tams/pull/173>

## Pros and Cons of the Options - for the `role` field

### Option R1: Make `role` a semi-structured field containing editorial purpose, media type and other details

Write an Application Note suggesting a naming convention for the `role` field, with a structured form that captures media type, editorial purpose and additional details.
This would be similar to the approach taken in the (now deprecated) [storage label AppNote](../appnotes/0009-storage-label-format.md).
Clients could either read the collection items and identify both type and purpose, or query the members of the collection and consider their labels/tags directly instead.

* Good, because it avoids a breaking change to the specification, instead only creating guidance.
* Good, because it makes `role` open-ended, allowing space for future change and expansion.
* Good, because it saves making additional API requests to get media type and other details of collection items.
* Bad, because it does not constrain the use of `role`, and clients may have to rely on human intervention.
* Bad, because it forces clients to handle and parse an un-enforced free-text field, which may be malformed as a result.

### Option R2: Replace `role` with a number of additional controlled fields

Change the specification to remove `role` and replace it with a more precise set of fields conveying the purpose of each element in the collection.

* Good, because it constrains and precisely describes what each item in a collection is for.
* Bad, because it requires a breaking change to the API, to provide a capability that can be achieved another way.
* Bad, because it requires work to fully specify all the possible purposes an item in a collection can fulfil.
* Bad, because it then constrains TAMS and requires a change as new purposes are identified.

### Option R3a: Use `role` solely for editorial purpose, and rely on other fields for other purposes

Use `role` primarily as a label to represent the editorial purpose of an item in a collection (broadly aligned with common usage).
Where a client wants to identify the type of a collection item, they can request the full details from the API.
For example if a collection contains multiple items of role "programme" the client could request all of those items by ID to find out one was video and one audio (or, subject to a draft ADR being accepted, make a direct query of `GET /flows?collected_by_id=...` and cross-reference the results with the collection listing).

* Good, because it aligns with current common usage of `role`.
* Good, because it avoids a breaking change to the specification.
* Good, becuause it does not introduce a semi-structured field and force clients to handle malformed data.
* Bad, because it forces clients to make additional requests (and possibly a somewhat complex cross-reference) to locate all the data they need.
  In particular a UI element displaying all the Sources in a store, the editorial purposes they contain and their media types would require an additional listing request per top-level Source.

### Option R3b: Use `role` as editorial purpose, use other queries for Flow/Source properties, surface `role` as a query param

As Option R3a, however `role` is added as an extra query parameter to the Flow and Source listing endpoints.
As a result, a client could request all the items of a specific role which are members of a particular collection (`GET /flows?collected_by_id=...&role=...`).

* Good, because it aligns with current common usage of `role`.
* Good, because it avoids a breaking change to the specification.
* Good, becuause it does not introduce a semi-structured field and force clients to handle malformed data.
* Bad, because it forces clients to make additional requests to locate all the data they need.
  In particular a UI element displaying all the Sources in a store, the editorial purposes they contain and their media types would require an additional listing request per top-level Source.
* Bad, because an item's role in a collection is a property of the collection, not the item, so the implementation is likely to be quite complex!

### Option R3c: Use `role` as editorial purpose, additionally surface `format` in collection

As Option R3a, however the `collects` property of a multi-essence Flow or Source gains an additonal property, `format` which is the `format` property of the collected item.
For example:

```json
[
    {
        "id": "f59a1785-b5bd-4829-afe0-7f65f9b335dd",
        "role": "programme",
        "format": "urn:x-nmos:format:video"
    },
    {
        "id": "7162d669-3230-4254-99d1-2c06f815d025",
        "role": "programme",
        "format": "urn:x-nmos:format:audio"
    },
    {
        "id": "2e285f91-6dff-4117-b26b-1ae749c5f5aa",
        "role": "audio_description",
        "format": "urn:x-nmos:format:audio"
    }
]
```

A client can directly identify the members of the collection directly.

* Good, because it aligns with current common usage of `role`.
* Good, becuause it does not introduce a semi-structured field and force clients to handle malformed data.
* Good, because it allows clients to get more of the salient information about a collection in a single request.
  It would allow the UI element suggested above to be built from a single listing request, for example.
* Neutral, because it changes the specification, albeit in a non-breaking way.

## Pros and Cons of the Options - for representing editorial purpose

### Option P1: Represent editorial purpose using DVB component descriptors

DVB uses the `stream_content`, `stream_content_ext` and `component_type` fields in the `component_descriptor` to describe the type of a Service.
These are described in [ETSI EN 300 468 pp 60-70](https://www.etsi.org/deliver/etsi_en/300400_300499/300468/01.19.01_60/en_300468v011901p.pdf).
TAMS could use the same descriptors, or their names.

* Good, because it is part of an established standard
* Bad, because the component types are represented as hex bytes (for carriage in the SDT table) and would need human-readable names
* Bad, because many of the types also include technical characteristics of content, making them unsuitable for use in Sources
* Bad, because the list is focused on distribution, so cannot contain aspects such as clean-feed video

### Option P2: Represent editorial purpose using MPEG-DASH roles

MPEG-DASH contains a role attribute for an `AdaptationSet`, which describes the purose of that particular track.
A number of values for that attribute are given in the specification (see ISO/IEC 23009-1:2022 section 5.8.5.5), covering the `main` content along with others such as `alternate`, `supplementary`, `commentary`, `description`, etc.
TAMS could use these descriptors for the table directly.

* Good, because it is part of an established standard
* Neutral, because the example use cases identified above could be represented, however some would be ambiguous, such as using `alternate` for clean-feed video
* Bad, because the list cannot be expanded beyond what is in the MPEG-DASH specification

### Option P3: Represent editorial purpose based on descriptions in the MovieLabs Ontology for Media Creation

The MovieLabs [Ontology for Media Creation](https://mc.movielabs.com/docs/ontology/) contains some definitions of the purpose of pieces of content.
Unfortunately it does not appear to represent differing purposes of video content, and for audio it refers to definitions in SMPTE ST 377-41.
It was not possible to acquire a copy of this SMPTE document at time of writing, although a version of those definitions are available in Appendix B of the [PDF version on the document](https://mc.movielabs.com/omc/Asset/Audio/ML_Ontology_Pt3C_Audio_v2.8.pdf).

* Good, because it is part of a controlled specification.
* Bad, because it relies on a document not available to the TAMS community.
* Bad, because video is not covered in the document.

### Option P4: Represent purpose of content using a list, as with tags

When describing the editorial purpose of an item in a collection, draw from a list of suggested types in an Application Note.
Allow new types to be added as they come up, in a similar process to tags.
Seed the initial list based on a combination of other specifications (including those above).

* Good, because it captures suggested names without constraining the purposes that a Flow or Source can be used for
* Good, because inspiration can be drawn from the other documents suggested, without being constrained by tem
* Good, because it is easy to add new items to the list
* Bad, because the list is open-ended and uncontrolled, which may lead to content using a mix of names
