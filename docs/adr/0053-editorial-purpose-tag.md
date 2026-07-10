---
status: "proposed"
---
# Editorial Purpose Tag

## Context and Problem Statement

[ADR0056: Roles in Collections](./0056-roles-in-collections.md) concluded that `role` did not make sense for storing editorial purpose, because it's a property of the Source (and by extension Flow) itself, rather than its membership in the collection.
This ADR considers where to store that information instead.

To give some motivating examples, a Source could contain:

* Programme video
* Signed video
* Clean-feed without graphics
* Programme audio
* Audio description
* Commentary
* Etc.

## Considered Options

* Option 1a: Represent editorial purpose as a field using DVB component descriptors
* Option 1b: Represent editorial purpose as a field using roles from MPEG-DASH
* Option 1c: Represent editorial purpose as a field based on descriptions in the MovieLabs Ontology for Media Creation
* Option 2: Represent purpose of content using a tag

## Decision Outcome

Chosen option: Option 2: Represent purpose of content using a tag, because it is not clear that any particular ontology or vocabulary is appropriate in all cases, and [Principle 5: TAMS does not implement a MAM](../../PRINCIPLES.md) applies here.
A user/content owner/broadcaster with strong opinions about how editorial purpose should be captured, should do so in a system designed for that purpose, and rely on the strong references in TAMS to cross-link the actual content.
However the tag is useful in "MAM-less" deployments where the amount of content is small, as a hint for interoperability and to potentially aid in searching across systems.

### Implementation

Implemented by [AppNote 0025: Editorial Purpose](../appnotes/0025-editorial-purpose.md) in <https://github.com/bbc/tams/pull/173>.

## Pros and Cons of the Options

### Option 1a: Represent editorial purpose as a field using DVB component descriptors

Add a new field to Flows and Sources called (for example) `editorial_purpose` that applies a controlled vocabulary drawn from DVB component descriptors.

DVB uses the `stream_content`, `stream_content_ext` and `component_type` fields in the `component_descriptor` to describe the type of a Service.
These are described in [ETSI EN 300 468 pp 60-70](https://www.etsi.org/deliver/etsi_en/300400_300499/300468/01.19.01_60/en_300468v011901p.pdf).
TAMS could use the same descriptors, or their names.

* Good, because it is part of an established standard
* Bad, because it is not clear this aligns with the "TAMS does not implement a MAM" principle
* Bad, because the component types are represented as hex bytes (for carriage in the SDT table) and would need human-readable names
* Bad, because many of the types also include technical characteristics of content, making them unsuitable for use in Sources
* Bad, because the list is focused on distribution, so cannot contain aspects such as clean-feed video

### Option 1b: Represent editorial purpose as a field using MPEG-DASH roles

As Option 1a, using MPEG-DASH role values instead.

MPEG-DASH contains a role attribute for an `AdaptationSet`, which describes the purose of that particular track.
A number of values for that attribute are given in the specification (see ISO/IEC 23009-1:2022 section 5.8.5.5), covering the `main` content along with others such as `alternate`, `supplementary`, `commentary`, `description`, etc.
TAMS could use these descriptors for the table directly.

* Good, because it is part of an established standard
* Neutral, because the example use cases identified above could be represented, however some would be ambiguous, such as using `alternate` for clean-feed video
* Bad, because it is not clear this aligns with the "TAMS does not implement a MAM" principle
* Bad, because the list cannot be expanded beyond what is in the MPEG-DASH specification

### Option 1c: Represent editorial purpose as a field based on descriptions in the MovieLabs Ontology for Media Creation

As Option 1a, using values from the MovieLabs [Ontology for Media Creation](https://mc.movielabs.com/docs/ontology/).

The ontology contains some definitions of the purpose of pieces of content.
Unfortunately it does not appear to represent differing purposes of video content, and for audio it refers to definitions in SMPTE ST 377-41.

* Good, because it is part of a controlled specification.
* Bad, because it is not clear this aligns with the "TAMS does not implement a MAM" principle.
* Bad, because video is not covered in the document.

### Option 2: Represent purpose of content using a tag

Add a tag along the lines of `editorial_purpose` to [AppNote 0003: Tag Names](../appnotes/0003-tag-names.md), with a list of suggested values.
Allow new values to be added as they come up, in a similar process to other tags.
Seed the initial list based on a combination of other specifications (including those above).

* Good, because it captures suggested names without constraining the purposes that a Flow or Source can be used for.
* Good, because inspiration can be drawn from the other documents suggested, without being constrained by them.
* Good, because it is easy to add new items to the list.
* Good, because tags are intended as a lightweight store of additional data for those times when, while TAMS is not a MAM, it can be a useful place to store MAM-like.
* Bad, because the list is open-ended and uncontrolled, which may lead to content using a mix of names.
