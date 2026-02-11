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

## Decision Drivers

* Roles must be set when creating a multi-essence collection.
* When viewing a multi-essence Source or Flow, only the list of IDs collected and roles are available: getting formats and tags requires another query.
* Items in a collection serve a variety of different purposes, and it is useful to have some commonality.

## Considered Options

* Option 1a: Provide guidance on how the free-text field `role` should be used
* Option 1b: Replace `role` with a number of additional controlled fields

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

## Pros and Cons of the Options

### Option 1a: Provide guidance on how the free-text field `role` should be used

Write an Application Note suggesting a naming convention for the `role` field, and that clients may also choose to query the members of the collection and consider their labels/tags directly instead.

* Good, because it avoids a breaking change to the specification, instead only creating guidance
* Good, because it makes `role` open-ended, allowing space for future change and expansion
* Bad, because it does not constrain the use of `role`, and clients may have to rely on human intervention

### Option 1b: Replace `role` with a number of additional controlled fields

Change the specification to remove `role` and replace it with a more precise set of fields conveying the purpose of each element in the collection.

* Good, because it constrains and precisely describes what each item in a collection is for.
* Bad, because it requires a breaking change to the API, to provide a capability that can be achieved another way.
* Bad, because it requires work to fully specify all the possible purposes an item in a collection can fulfil.
* Bad, because it then constrains TAMS and requires a change as new purposes are identified.

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
