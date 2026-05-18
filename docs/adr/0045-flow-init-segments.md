---
status: "proposed"
---
# Support for init Segments in Flows

## Context and Problem Statement

Various media formats employ initialisation segments (aka init segments) for communicating parameters required to configure decoders.
Notably, CMAF-compatible formats such as MPEG DASH and Fragmented MP4 (fMP4).
Init segments are normally communicated via a manifest, alongside media segments.
The decoder will fetch and process the init segment, before identifying the required media segments (which may be mid-stream) and fetching and processing those.

From a TAMS perspective, init segments are not normally associated with any particular point of time.
A client must be able to write/read, or construct, an init segment independently of the timeline.

## Decision Drivers

We would like to:

* support TAMS features (e.g. edit-by-reference) as fully as possible
* be compatible with as many decoders/players as possible
* place as little burden on implementations as possible with TAMS-specific functionality
* have no/minimal impact on existing (non-init segment based) implementations
* re-use existing patterns/functionality where possible/practical
* maintain, as far as possible, the "independently decodable Objects" property of TAMS
* allow the use of existing init segment extensions (e.g. C2PA)
* avoid specifying Flow parameters that are format-specific

## Considered Options

* Option 1: Generate init segments from essence parameters
* Option 2: Significantly expand essence parameters to fully capture everything
* Option 3: Create a Flow Segment with a never timerange for the init segment
* Option 4: Make the init segment a Flow-level property for which a URL can be generated
* Option 5: Make the init segment an object-level property, which can be uploaded and have a URL generated
* Option 6: Have a Flow that is the init segment Flow
* Option 7: Put the init segment somewhere on the TAMS API instead of as an object (e.g. as a base64 blob)
* Option 8: Embed the init segment in every Object

## Decision Outcome

Chosen option: Option 5: Make the init segment an object-level property, which can be uploaded and have a URL generated.

Options 1, 2, 3, and 4 would not allow for Flows which have multiple init segments.
This would place additional restrictions on workflows that TAMS interfaces with, or would require transformation to/from a single-init segment rendition where multiple init segment renditions are required elsewhere.
Examples of such workflows are those which use multi-period manifests, and those which use certain profiles of C2PA.
Additionally, edit-by-reference workflows would be unduly restricted by the need for a single init segment per Flow.

Option 1, 2, 3, and 7 were considered particularly undesirable in terms of how they interacted with the TAMS data model, clashed with existing patterns, or would have a poor developer experience.

Option 6 would require implementations generic operations (e.g. store transfer) to have specific understanding/behaviour of media types to operate correctly.
It may also break existing implementations of such functionality silently in some cases (e.g. media segments copied without init segments), or result in unexpected behaviour.

Option 8 would again place restrictions on workflows that TAMS interfaces with, or would require transformation to/from an embedded-segment rendition.
Such an approach was also identified as being expressly prohibited by some media formats.
Real-world issues were also identified regarding processing load, and smoothness of playback with some player/decoder implementations where superfluous init segments are provided.

Option 5 provides little/no restrictions on broader workflows.
It provides good backwards compatibility.
It provides good feature compatibility with the likes of edit-by-reference.
It provides minimal burden on client implementations.
It re-uses existing patterns, keeping the burden on service implementations as low as possible.

### Implementation

Implemented by <https://github.com/bbc/tams/pull/167>.

## Pros and Cons of the Options

### Option 1: Generate init segments from essence parameters

This option would see reading clients (or the store) generate their own init segments based on the existing technical metadata in the Flow metadata.
This is likely not possible with TAMS currently.
The TAMS API likely does not capture all metadata media formats may need to include in init segments.

* Good, because it requires no changes to the API specification
* Bad, because initial research indicates this will not be possible due to missing metadata
* Bad, because it requires a potentially complex implementation that requires in-depth knowledge of the structure of init segments and significant domain expertise
* Bad, because extensions such as C2PA metadata may need to be re-created on ingest due to the sequence of init and media segments changing

### Option 2: Significantly expand essence parameters to fully capture everything

This option would see Option 1 extended to include the addition of required parameters to Flow metadata.

* Bad, because it will likely require significant additions to Flow technical metadata
* Bad, because it will likely require the addition of format specific parameters to Flow technical metadata
* Bad, because it requires a potentially complex implementation that requires in-depth knowledge of the structure of init segments and significant domain expertise
* Bad, because extensions such as C2PA metadata may need to be re-created on ingest due to the sequence of init and media segments changing

### Option 3: Create a Flow Segment with a never timerange for the init segment

The TAMS TimeRange format has a special "never" value - `()`.
This currently has no meaning for Flow Segments, as media segments always have a duration.
Init segments can be considered to have no duration.
This option would see the never TimeRange used to represent init segments.

* Good, because it requires little/no spec changes
* Good, because it doesn't require format-specific Flow parameters
* Neutral, because extensions such as C2PA metadata should be supported as the sequence of init and media segments isn't changed
* Bad, because it doesn't allow for different init segments for different parts of the Flow
  * Relevant formats support multiple init-segments via features such as "multi-Period" manifests
  * Some relevant formats may use init segments to signal minor changes to encoding parameters
* Bad, because the approach is somewhat unintuitive
* Bad, because it may result in unexpected behaviour with existing TAMS implementations

### Option 4: Make the init segment a Flow-level property for which a URL can be generated

This option would see the init segment managed via the existing Object CRUD mechanisms.
But rather than being registered against a Flow Segment, it would be registered against a new Flow property.
Existing Object patterns would be used for upload, URL generation, re-use, delete, etc.
Like Flow Segments, different Flows could re-use the same init Object.
Implementations might use the init segment's Object ID to determine the compatibility of Flow Segments in edit-by-reference workflows.

* Good, because it doesn't require format-specific Flow parameters
* Good, because it re-uses existing patterns/mechanisms
* Neutral, because it requires a backwards-compatible addition to the spec
* Neutral, because extensions such as C2PA metadata should be supported as the sequence of init and media segments isn't changed
* Bad, because it doesn't allow for different init segments for different parts of the Flow
  * Relevant formats support multiple init-segments via features such as "multi-Period" manifests
  * Some relevant formats may use init segments to signal minor changes to encoding parameters

### Option 5: Make the init segment an object-level property, which can be uploaded and have a URL generated

As with Option 4, this option would see the init segment managed via the existing Object CRUD mechanisms.
Rather than associating the init Object with the Flow, this option would see it associated with each Media Object.
A change in the init segment's Object ID may be used to determine a need to re-provision the init segment in the consuming client.

* Good, because it doesn't require format-specific Flow parameters
* Good, because it re-uses existing patterns/mechanisms
* Good, because it allows for different init segments for different parts of the Flow
  * Relevant formats support multiple init-segments via features such as "multi-Period" manifests
  * Some relevant formats may use init segments to signal minor changes to encoding parameters
* Neutral, because it requires a backwards-compatible addition to the spec
* Neutral, because extensions such as C2PA metadata should be supported as the sequence of init and media segments isn't changed
* Bad, because it will result in a significant increase in Object metadata which makes up a large proportion of data stored in TAMS

### Option 6: Have a Flow that is the init segment Flow

This option would see a new init segment Flow type.
An init Flow would be associated with the media Flow.
Init segments would be assigned the TimeRange over which they are valid in the associated media Flow.
This would allow for multiple init segments to be applied to different parts of the media Flow's timeline.

* Good, because it doesn't require format-specific Flow parameters
* Good, because it re-uses existing patterns/mechanisms
* Good, because it allows for different init segments for different parts of the Flow
  * Relevant formats support multiple init-segments via features such as "multi-Period" manifests
  * Some relevant formats may use init segments to signal minor changes to encoding parameters
* Neutral, because it requires a backwards-compatible addition to the spec
* Neutral, because it may be unintuitive
* Neutral, because it would require open-ended Flow Segments to support live Flows
* Neutral, because extensions such as C2PA metadata should be supported as the sequence of init and media segments isn't changed
* Bad, because it requires Objects from multiple Flows (init segment Flow, and media segment Flow) to decode a give piece of media

### Option 7: Put the init segment somewhere on the TAMS API instead of as an object (e.g. as a base64 blob)

As with Options 4, 5, or 6.
But the init segment would be stored as a base 64 encoded blob (or similar) that may be held in the backend database, instead of as file stored in an object store.

In addition to the base options:

* Bad, because it would represent a new pattern where one isn't strictly required
* Bad, because it would require a different GET path to media segments
* Bad, because it would likely require additional work on the part of clients to construct a virtual file for the init segment to pass to decoders/players

### Option 8: Embed the init segment in every Object

As with Option 5, but with the init segment embedded in the Object file itself, rather than as a property against the Object.
This would make each Object entirely independently decodable, maintaining this important property of TAMS.
Relevant formats have a concept of "self-initialising" media segments.
But these are, in at least some formats, explicitly not allowed for segmented media such as is used in TAMS.
And are only permitted for playlist-style use cases where a media segment is used to contain a full file.

* Good, because it doesn't require format-specific Flow parameters
* Good, because it re-uses existing patterns/mechanisms
* Good, because it requires no changes to the API specification
* Good, because it allows for different init segments for different parts of the Flow
  * Relevant formats support multiple init-segments via features such as "multi-Period" manifests
  * Some relevant formats may use init segments to signal minor changes to encoding parameters
* Bad, because media using extensions such as C2PA metadata may need to be re-encoded/re-packaged on ingest due to the sequence of init and media segments changing
* Bad, because it will result in an increase in the size of Objects, which makes up a large proportion of data stored in TAMS
  * Such an increase is likely to be minor for individual Objects, but significant in larger deployments with relatively small Segment sizes
  * Note: This point is in comparison to the other Options in the ADR, rather than to the current situation in the TAMS ecosystem where equivalent metadata is already stored in Objects
* Bad, because this approach may result in un-needed overheads or even interrupted playback in some player implementations
  * Some relevant implementations of player technologies, such as Media Source Extensions, are known to re-initialise decoders on (superfluous) new init segments which may result in disruption to playback

### Option 9: Do not add support for init segments

Many/all of the above options require significant changes to how the TAMS API is used, or requires formats such as fMP4 to be used in non-standard ways.
This may lead to fragmentation of the TAMS ecosystem, or require fMP4 codecs to be modified in a manner that requires significant in-depth domain knowledge.
We have, however, seen multiple off-spec extensions to the TAMS specification to add init-segment support which itself exacerbates the issue of fragmentation of the TAMS ecosystem.

* Good, because it encourages TAMS interoperability by maintaining a small number of workflow variations.
* Neutral, because we would explicitly not support a format commonly used in the media industry
  * If the way the format would be supported would be non-standard from an fMP4 point of view, TAMS support may bring its own issues - hence "neutral"
* Bad, because this option may persist the existing situation with off-spec extensions
