---
status: "rejected"
---
# Flow and Source References

## Context and Problem Statement

Media Flows are brought into existence after being captured or created.
The Flows can then be re-used and processed in media workflows to create new Flows.

An ancestry relationship is defined to relate a time range of a given Flow or Source to a time range of another Flow or Source.

The time range could cover eternity.
The time range will generally be on the presentation timeline rather than the decode timeline, i.e. it is independent of the coding used that may alter the timing because of frame re-ordering.
Ancestry relationships may overlap in time, e.g. if multiple audio Flows were mixed.

The ancestry relationship defines a relationship type.
One or more base types could be defined (e.g. "derived_from") with an option to extend once.
This would allow operations to be performed using the base type whilst enabling additional information for specific applications.
Additional properties or tags can provide further information for the relationship.

It is useful to be able to retrace the ancestry of a Flow to allow

* metadata such as rights to be traced back to the originating Flows
* new Flows to be created by using ancestry information from an existing Flow

## Decision Drivers

* The concern here is primarily with a basic ancestry relationship for Flows and Sources.
  * The details of the derivation are not important and are better handled by media composition languages and formats.
  * Other relationships such as multiplexing and synchronisation are not considered here.
* The approach should try avoid going too far beyond the core functionailty of TAMS.

## Considered Options

* Option 1: Annotate Flow to indicate the ancestry relationship with other Flows.
* Option 2: Annotate Flow Segments to indicate the ancestry relationship with other Flow Segments that reference the same media object.
* Option 3: Annotate Flow Segments to indicate the ancestry relationship with other Flows or Sources.
* Option 4: Define a Flow Reference and Source Reference that indicate the ancestry relationship to other Flows or Sources.

## Pros and Cons of the Options

### Option 1: Annotate Flow to indicate the ancestry relationship with other Flows

Flow properties and tags could be added as required to indicate ancestry relationships (for time range eternity).
The Flow also already includes a `generation` property that indicates the number of re-encodings (generations) that were performaned to produce the Flow.

* Good, because it is easy to use tags or properties as required per application
* Bad, because it can only be used to define relationships for the complete Flow and not time ranges

### Option 2: Annotate Flow Segments to indicate the ancestry relationship with other Flow Segments that reference the same media object

Flow Segments represent a time range of media samples that are stored in a media object.
Multiple Flow Segments can reference the same media object and this implicitly defines a shared media relationship between the Flows that the Flow Segments belong to.
Properties or tags could be added to Flow Segment to allow further refinement to the relationship.

* Good, because the media object re-use relationship is already present in the TAMS data structures
* Bad, because the relationship is limited to other Flows that are also reference media objects in the store
* Bad, because the relationship is limited to other Flows using the same encoding
* Bad, because the relationship is limited to other Flows using the same segmentation

### Option 3: Annotate Flow Segments to indicate the ancestry relationship with other Flows or Sources

Flow Segments are extended with properties and / or tags that reference other Flows or Sources.
The properties would define the time range of the target Flow or Source and the specifics of the relationship.

* Good, because it extends the existing Flow Segment data structure
* Bad, because the relationship is limited to the time range covered by the Flow Segment that is determined by the encoding and segmentation choices made

### Option 4: Define a Flow Reference and Source Reference that indicate the relationship to other Flows or Sources

A Flow Reference defines a relationship from a time range of a Flow to a time range of another Flow or Source.
A Source Reference defines a relationship from a time range of a Source to a time range of another Source.
The Flow and Source References includes properties and tags to define the specifics of the relationship.

* Good, because the relationship can be defined independently of how the Flow is segmented or encoded into media objects
* Good, because the relationships can be defined even when media samples are not (yet) present in the store
* Good, because it allows the relationships to be set and processed independently of the Flow Segments
* Neutral, because the Flow and Source References are not required to manage storage of the media, but these relationships need to be held somewhere

## More Information

### TAMS/AWS Workshop Discussion - 13th February 2024

A discussion about this proposal took place during the TAMS/AWS workshop on 13th February 2024, with the BBC R&D TAMS team, BBC B&EUT architects and AWS Solution Architects.

The discussion concluded that in the general case, this type of ancestry should be represented using Source<->Source relationships and/or some sort of EDL format such as OpenTimelineIO or AAF and/or should be handled inside a MAM.

Management of complex Source<->Source relationships isn't made possible in an effective way by any of the proposals in this ADR, which only really improves the "lightweight copies" use case.
For the simple case where you want to make a subclip without modification, it probably makes more sense to store a Source (or Flow) ID and a timerange, e.g. inside a MAM.
Further to [Deletion of Content and IDs](https://github.com/bbc/tams/blob/main/docs/adr/0004-content-deletion.md) it is assumed such a MAM would also arbitrate deletion requests to avoid removing content needed by a subclip.

In a proof-of-concept setting where no MAM is used, it may be useful to be able to create a separate Flow (pointing at the same media objects).
In this case it is still possible to do so (and re-time the Flow if needed), however no reference is preserved to the original Flow.
In such a case, tags could be used to identify the original Source (e.g. an `originating_id` and `originating_timerange` tag).
In general it was proposed that the TAMS team monitor how tags are used in practice, and revisit this proposal if that usage is common.
A future Application Note will describe commonly used tags and their meaning.
For these reasons, this ADR proposal is rejected.
