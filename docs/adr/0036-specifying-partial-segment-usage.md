---
status: "proposed"
---
# Specifying Partial Segment Usage

## Context and Problem Statement

TAMS contains a mechanism to re-use segments, as described in the [Flow and Media Timelines](https://github.com/bbc/tams/blob/9125165/README.md#flow-and-media-timelines) section of the README.
Naturally entire segments can be used, however it is also possible to use only part of a segment, and readers are expected to handle discarding un-used parts of a segment as needed.
Identifying the parts to keep can currently be achieved in two ways: either by applying `ts_offset` to map the media object timeline into the Flow timeline, then using the `timerange` to filter to the desired grains, or using `sample_offset` and `sample_count` to discard samples.
A better description of this is in the README at <https://github.com/bbc/tams?tab=readme-ov-file#flow-and-media-timelines>.
However it is not clear that the second method is usefully differentiated from the first.

## Decision Drivers

* TAMS readers need to be able to identify which samples to return to a consuming client
* In some cases temporal re-ordering is applied, so the media object is in decode order, but the `timerange`, `sample_offset` and `sample_count` all apply in presentation order
* TAMS is intended to support a variety of media container formats, so the solution should be generally applicable
* Theoretically partial audio segments can be selected on individual samples, not just coded frames

## Considered Options

* Option 1: Retain both sample-based and time-based selection mechanism
* Option 2: Remove sample-based mechanism
* Option 3a: Store timerange of media object and use time-based selection with skip and duration
* Option 3b: Store timerange of media object, optionally present skip details
* Option 3c: Store timerange of media object, optionally provide it on Flow Segments
* Option 3d: Store timerange of media object, optionally provide it on Flow Segments, deprecate offset/count

## Decision Outcome

Chosen option: Option 3d, because Option 3 allows working entirely in terms of time, and avoids confusion and difficulty when accounting for gaps, while accounting for all known practical implementations.
Option 3d is chosen because it provides the most useful piece of information from which other timings can be trivially calculated, without adding undue load to the API.
In addition, it avoids making this a breaking change and breaking existing implementations, by retaining the previous behaviour.

### Implementation

Implemented by <https://github.com/bbc/tams/pull/147>

## Pros and Cons of the Options

### Option 1: Retain both sample-based and time-based selection mechanism

Retain the existing combination of both `sample_offset`/`sample_count` along with the ability to calculate grains to use vs discard based on `timerange` and `ts_offset`.
Stipulate throughout the documentation that if the defaults (`sample_offset=0` and `sample_count` is the entire segment) are not valid because part of the segment has been used, then they must be set correctly.
Call out in documentation that either method can be used by a reader.

* Good, because it may be easier to select the correct grains by counting and discarding (when temporal re-ordering is not applied).
  For example it may be possible to avoid parsing/demuxing the container to extract timestamps, if Flow timing is carried out-of-band
* Good, because it supports simple "clip list" based implementations that can only count decoded media units and not read the object's internal timing
* Good, because it avoids a change to the existing API
* Neutral, because it works for containers without any internal timing where the Flow doesn't have a rate, however there are no current known use cases (or containers!) with this property
* Bad, because a writer has to do additional work to identify the correct `sample_offset`/`sample_count` settings when re-using segments, which may require it to download and parse the media
* Bad, because this is even more difficult if grains have variable duration/gaps and are out of order: a writer must first switch them to presentation order, then filter on the desired TimeRange and count
* Bad, because it duplicates a piece of data which adds complexity and risk to keep it in sync
* Bad, because it adds complexity in having two methods to achieve the same goal, without clear benefit to that flexibility

### Option 2: Remove the sample-based selection mechanism

Remove `sample_offset` and `sample_count` from the API (possibly by first deprecating using the JSON Schema [`deprecated`](https://json-schema.org/draft/2020-12/json-schema-validation#name-deprecated) flag).
Make partial-segment re-use via `timerange`/`ts_offset` clearer in the documentation.
Readers will then need to calculate the timestamp for each grain on the Flow timeline by applying `ts_offset` to the media object's internal timeline, then check whether that timestamp is contained by the segment's `timerange`.

* Good, because it avoids un-necessary work for writers of partial-segment Flows
* Good, because it removes duplicated information and potential for an error condition
* Neutral, because it forces the use of either containers with some kind of internal timing or Flows with a rate and no gaps inside the objects (although gaps between segments is still possible)
* Bad, because it forces readers to parse the internal timing of media objects (which may be impossible without modifying underlying libraries, such as Ffmpeg)
* Bad, because it may break existing implementations or make them more complex in some cases

_Note:_ if the container has no internal timing, however the Flow has a rate and it can be assumed to have no gaps, the grain timestamp can still be calculated by computing its timestamp at the relevant rate from the beginning of the object, then mapping that into the Flow timeline using `ts_offset`.
In that case the media object timestamp for the first grain is `0:0`, so when the object was newly written and entirely used by a Flow Segment, `segment.ts_offset = segment.timerange.start`.

### Option 3a: Store timerange of media object and use time-based selection with skip and duration

Instead of using `sample_offset` and `sample_count`, provide `skip` and `duration` fields on each Flow Segment, describing how much time to skip from the beginning of the media object, and the duration after that of the Flow Segment.
When a media object is registered to a Flow for the first time, clients can optionally provide a `object_timerange`: the timerange contained within the object (e.g. the timerange of a Flow Segment consuming the entire object if `ts_offset=0`).
This field can be made optional, because the specification already expects that for newly-written media objects "all samples in the object SHOULD be used by the Segment", therefore if not set at first registration, it can be assumed the `object_timerange = segment.timerange`.

A TAMS API implementation can calculate the correct values for `skip` and `duration` by transforming the Flow Segment `timerange` into the media timeline (`timerange - ts_offset`) and then comparing it to the `object_timerange`.

* Good, because implementations tend to work in terms of time, not samples
* Good, because it makes sub-segment handling much easier for readers that cannot inspect the media timing
* Good, because it avoids writers needing to re-calculate offsets and counts
* Good, because it handles gaps without requiring even more work from writers
* Good, because readers don't need to convert offsets and counts to time (with potential edge cases around Flows with no rate)
* Good, because it ties the required piece of information about the media object (the `object_timerange`) to the object itself
* Neutral, because it will be a breaking change, but a relatively easy one to account for
* Neutral, because it forces the use of either containers with some kind of internal timing or Flows with a rate and no gaps inside the objects (although gaps between segments is still possible)
* Bad, because it creates more work for the API implementation to handle each Flow Segment request
* Bad, because the `duration` data is extraneous - it is already present in the segment `timerange`

### Option 3b: Store timerange of media object, optionally present skip details

As Option 3a, except `skip` and `duration` are only returned when a query string parameters `?include_skip_duration=true` is set.

Benefits and drawbacks as above, except the following item:
> Bad, because it creates more work for the API implementation to handle each Flow Segment request

Is replaced with:
> Bad, because it adds more complexity to the API implementation

### Option 3c: Store timerange of media object, optionally provide it on Flow Segments

As Option 3a, except `skip` and `duration` are removed and `object_timerange` is returned directly on a Flow Segment when `include_object_timerange=true` is set.

Benefits and drawbacks as Option 3a, except the following item:
> Bad, because it creates more work for the API implementation to handle each Flow Segment request

Is replaced with:
> Neutral, because it avoids calculation work on the part of the API implementation, moving it to the client

### Option 3d: Store timerange of media object, optionally provide it on Flow Segments, deprecate offset/count

As Option 3a, except `skip` and `duration` are removed and `object_timerange` is returned directly on a Flow Segment when `include_object_timerange=true` is set.
Additionally unlike Option 3c, deprecate `sample_offset` and `sample_count` rather than removing outright, to avoid a breaking change.
Instead if present/given, `sample_offset` and `sample_count` behave as before, however implementations should use the new timerange field.

Benefits and drawbacks as Option 3a, except the following item:
> Bad, because it creates more work for the API implementation to handle each Flow Segment request

Is replaced with:
> Neutral, because it avoids calculation work on the part of the API implementation, moving it to the client

And the following item is removed:
> Neutral, because it will be a breaking change, but a relatively easy one to account for

## Appendix: Possible Implementations

This segment summarises some approaches taken or theorised by TAMS readers to correctly implement partial segment usage.
Note that it is possible to build a naïve TAMS reader that works without supporting partial segment usage: for example any implementation based on HLS (because HLS has no mechanism to consume only part of a fragment).

### Ffmpeg Patch

An internal BBC R&D proof-of-concept patch to Ffmpeg uses `timerange` and `ts_offset`, by rewriting the `pkt->pts` based on `ts_offset` and then setting the discard flag on any packet not within the Flow Segment `timerange`.

Attempts to implement the same patch using `sample_offset` and `sample_count` ran into difficulties because the segment details are available to the demuxer (in `libavformat`) but the packets are in decode order: they are only returned to presentation order in the decoder (in `libavcodec`), so the offsets and counts would have to be converted to timestamps anyway: this poses a problem if there are gaps in the segment.

### Ffmpeg Workers

The implementation used by the Ffmpeg worker Lamdbas in <https://github.com/aws-samples/time-addressable-media-store-tools> is to set the `-ss` flag for the number of seconds to skip at the beginning of the segment, and the `-t` flag for how much of the segment to consume, then use `-output_ts_offset` to undo the effects of skipping part of the segment.
This works because the worker handles each segment independently (rather than a player or similar, that processes the entire Flow).
Unfortunately the `-ss` and `-t` flags only accept time, not sample/frame counts.

See <https://github.com/aws-samples/time-addressable-media-store-tools/blob/f48892b/backend/components/ingest-ffmpeg/functions/ffmpeg-worker/app.py#L50-L67> for the implementation.

### File export service

A file export service with the ability to skip parts of the input material could in principle produce an HLS manifest, along with a list of which parts of that manifest are skipped because they are not used in the Flow.
As a result TAMS support could be implemented with very little work to the underlying media processing, by using the offset and count to calculate the correct time.

Unfortunately this requires calculating the time left in the media object after the segment, which is not possible without knowing how long the segment is, something not exposed by the TAMS API.
