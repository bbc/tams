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
* allow the use of existing init segment extensions (e.g. C2PA)
* avoid specifying Flow parameters that are format-specific

## Considered Options

* {title of option 1}
* {title of option 2}
* {title of option 3}
* … <!-- numbers of options can vary -->

## Decision Outcome

Chosen option: "{title of option 1}", because
{Justification, e.g., only option which resolves requirements, or comes out best (see below)}.

<!-- This is an optional element. Feel free to remove. -->
### Implementation

{Once the proposal has been implemented, add a link to the relevant PRs here}

<!-- This is an optional element. Feel free to remove. -->
## Pros and Cons of the Options

### Option 1: Generate init segments from essence parameters

This option would see reading clients (or the store) generate their own init segments based on the existing technical metadata in the Flow metadata.
This is likely not possible with TAMS currently.
The TAMS API likely does not capture all metadata media formats may need to include in init segments.

* Good, because it requires no changes to the API specification
* Bad, because initial research indicates this will not be possible due to missing metadata
* Bad, because it requires a potentially complex implementation that requires in-depth knowledge of the structure of init segments and significant domain expertise

### Option 2: Significantly expand essence parameters to fully capture everything

This option would see Option 1 extended to include the addition of required parameters to Flow metadata.

* Bad, because it will likely require significant additions to Flow technical metadata
* Bad, because it will likely require the addition of format specific parameters to Flow technical metadata
* Bad, because it requires a potentially complex implementation that requires in-depth knowledge of the structure of init segments and significant domain expertise

### Option 3: Create a Flow Segment with a never timerange for the init segment

The TAMS TimeRange format has a special "never" value - `()`.
This currently has no meaning for Flow Segments, as media segments always have a duration.
Init segments can be considered to have no duration.
This option would see the never TimeRange used to represent init segments.

* Good, because it requires little/no spec changes
* Good, because it doesn't require format-specific Flow parameters
* Neutral, because it doesn't allow for different init segments for different parts of the Flow
  * Note: It is not clear we have a real use case for this as a new init segment likely means a change to the technical parameters, which requires a new Flow in TAMS
  * Initial testing indicates common fMP4/DASH players do not support multiple init segments
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
* Neutral, because it doesn't allow for different init segments for different parts of the Flow
  * Note: It is not clear we have a real use case for this as a new init segment likely means a change to the technical parameters, which requires a new Flow in TAMS
  * Initial testing indicates common fMP4/DASH players do not support multiple init segments
* Netural, because it requires a backwards-compatible addition to the spec

### Option 5: Make the init segment an object-level property, which can be uploaded and have a URL generated

As with Option 4, this option would see the init segment managed via the existing Object CRUD mechanisms.
Rather than associating the init Object with the Flow, this option would see it associated with each Media Object.
A change in the init segment's Object ID may be used to determine a need to re-provision the init segment in the consuming client.

* Good, because it doesn't require format-specific Flow parameters
* Good, because it re-uses existing patterns/mechanisms
* Neutral, because it allows for different init segments for different parts of the Flow
  * Note: It is not clear we have a real use case for this as a new init segment likely means a change to the technical parameters, which requires a new Flow in TAMS
  * Initial testing indicates common fMP4/DASH players do not support multiple init segments
* Netural, because it requires a backwards-compatible addition to the spec
* Bad, because it will result in a significant increase in Object metadata which makes up a large proportion of data stored in TAMS

### Option 6: Have a Flow that is the init segment Flow

This option would see a new init segment Flow type.
An init Flow would be associated with the media Flow.
Init segments would be assigned the TimeRange over which they are valid in the associated media Flow.
This would allow for multiple init segments to be applied to different parts of the media Flow's timeline.

* Good, because it doesn't require format-specific Flow parameters
* Good, because it re-uses existing patterns/mechanisms
* Neutral, because it allows for different init segments for different parts of the Flow
  * Note: It is not clear we have a real use case for this as a new init segment likely means a change to the technical parameters, which requires a new Flow in TAMS
  * Initial testing indicates common fMP4/DASH players do not support multiple init segments
* Netural, because it requires a backwards-compatible addition to the spec
* Neutral, because it may be unintuitive
* Neutral, because it would require open-ended Flow Segments to support live Flows

### Option 7: Put the init segment somewhere on the TAMS API instead of as an object (e.g. as a base64 blob)

As with Options 4, 5, or 6.
But the init segment would be stored as a base 64 encoded blob (or similar) that may be held in the backend database, instead of as file stored in an object store.

In addition to the base options:

* Bad, because it would represent a new pattern where one isn't strictly required
* Bad, because it would require a different GET path to media segments
* Bad, because it would likely require additional work on the part of clients to construct a virtual file for the init segment to pass to decoders/players
