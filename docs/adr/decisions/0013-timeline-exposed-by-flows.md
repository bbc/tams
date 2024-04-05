---
status: "proposed"
---
# Timeline exposed by Flows

## Context and Problem Statement

The TAMS API specification and associated README do not explicitly indicate how the timings relate to timestamps inside media object files: the [README](https://github.com/bbc/tams/blob/16ea401/README.md#flow-and-media-timelines) simply calls it the "media timeline".
A number of common codecs support temporal re-ordering which creates multiple timelines, for example the decode and presentation order of frames of video.
To avoid confusion between clients and when moving between codecs, the TAMS API should define the relationship between these timelines.

## Decision Drivers

* All Flows of a Source share a common timeline, regardless of how they are coded, and clients need a common understanding to avoid "jumps" when changing codec
* TAMS should aim to be flexible, while aligning with how other media formats behave (_e.g._ taking inspiration from MPEG-DASH and HLS)

## Considered Options

* Option 1: Make the Flow timeline represent the decode timeline
* Option 2: Make the Flow timeline represent the presentation timeline
* Option 2a: Additionally recommend Flow Segments contain whole GOPs or equivalent

## Decision Outcome

Chosen option: Option 2a: Make the Flow timeline represent the presentation timeline, and contain whole GOPs or equivalent, because it avoids problems where timing "jumps" when changing codec, without unduly complicating client implementations.

### Implementation

Implemented by <https://github.com/bbc/tams/pulls/37>

## Pros and Cons of the Options

### Option 1: Make the Flow timeline represent the _decode_ timeline

Explicitly document that the Flow timeline represents the _decode_ timeline.
Clients are expected to start reading either from the position of interest on the Flow timeline, or the first segment preceding that where `key_frame_count` is greater than 0.
In either case, a client may need to read an earlier segment in order to locate the timestamp of interest due to temporal re-ordering.
This is how the BBC R&D proof-of-concept implementation works at time of writing, largely for historical reasons.

* Good, because regardless of Flow Segment size, the ["media timeline"](https://github.com/bbc/tams/blob/16ea401/README.md#flow-and-media-timelines) inside the segment contains monotonically increasing timestamps.
* Good, because it aligns with how the existing proof-of-concept implementation works.
* Bad, because it's the opposite of how chunked streaming formats like MPEG-DASH and HLS work, which refer to the presentation timeline.
* Bad, because a timestamp on a Source should point to the same content in all Flows of that Source, but the same time on the decode timeline may reference different frames on the presentation timeline, for example if one Flow is intra-coded and another uses a temporally re-ordered inter-coding scheme..
* Bad, because a client may need to read and inspect additional media in order to locate the point of interest.

### Option 2: Make the Flow timeline represent the _presentation_ timeline

Explicitly document that the Flow timeline represents the _presentation_ timeline.
As with Option 1, a client may have to read backwards from a point of interest to retrieve enough material to decode the segment, _e.g._ to find a stream access point.
In addition short Flow Segments will naturally sort into presentation order, and may need to be sorted into decode order (by inspecting their internal media timeline, or adding additional properties) before being decoded.

* Good, because most clients are interested in the presentation timeline - _e.g._ the actual video frames and audio samples, and this naturally aligns the API with that.
* Good, because it matches how MPEG-DASH and HLS work, which refer to the presentation timeline.
* Good, because regardless of codec the mapping to decoded essence remains consistent.
* Bad, because a client may need to read and inspect additional media in order to locate the point of interest.
* Bad, because a client may have to re-order coded media units across multiple Flow Segments before feeding them into the decoder.

### Option 2a: ...recommend that Flow Segments contain whole GOPs or equivalent

Use the _presentation_ timeline as in Option 2, with the addition of recommending that Flow Segments contain complete GOPs, or equivalent decodable units.
This is akin to the MPEG-DASH requirement that each segment start with a Stream Access Point (SAP).

* Good, because a client should not need to re-order coded media units across multiple Flow Segments before feeding them into the decoder.
* Good, because it is likely each Flow Segment will become independently decodable.
  However for some coding schemes such as open GOP, it may still be necessary to seek further back and clients should implement the functionality.
* Bad, because it increase latency to the size of a GOP, however applications can tune that by reducing the GOP length of their encoder, or for example using an intra-frame codec.
