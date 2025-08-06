---
status: "proposed"
---
# Specifying Partial Segment Usage

## Context and Problem Statement

TAMS contains a mechanism to re-use segments, as described in the [Flow and Media Timelines](https://github.com/bbc/tams/blob/9125165/README.md#flow-and-media-timelines) section of the README.
Naturally entire segments can be used, however it is also possible to use only part of a segment, and readers are expected to handle discarding un-used parts of a segment as needed.
Identifying the parts to keep can currently be achieved in two ways: either by applying `ts_offset` to map the media object timeline into the Flow timeline, then using the `timerange` to filter to the desired grains, or using `sample_offset` and `sample_count` to discard samples.
A better description of this is in a draft README amendment in <https://github.com/bbc/tams/pull/141>.
However it is not clear that the second method is usefully differentiated from the first.

## Decision Drivers

* TAMS readers need to be able to identify which samples to return to a consuming client
* In some cases temporal re-ordering is applied, so the media object is in decode order, but the `timerange`, `sample_offset` and `sample_count` all apply in presentation order
* TAMS is intended to support a variety of media container formats, so the solution should be generally applicable
* Theoretically partial audio segments can be selected on individual samples, not just coded frames

## Considered Options

* Option 1: Retain both sample-based and time-based selection mechanism
* Option 2: Remove sample-based mechanism

## Decision Outcome

Chosen option: TBD, because
{Justification, e.g., only option which resolves requirements, or comes out best (see below)}.

### Implementation

{Once the proposal has been implemented, add a link to the relevant PRs here}

## Pros and Cons of the Options

### Option 1: Retain both sample-based and time-based selection mechanism

Retain the existing combination of both `sample_offset`/`sample_count` along with the ability to calculate grains to use vs discard based on `timerange` and `ts_offset`.
Stipulate throughout the documentation that if the defaults (`sample_offset=0` and `sample_count` is the entire segment) are not valid because part of the segment has been used, then they must be set correctly.
Call out in documentation that either method can be used by a reader.

* Good, because it may be easier to select the correct grains by counting and discarding (when temporal re-ordering is not applied).
  For example it may be possible to avoid parsing/demuxing the container to extract timestamps, if Flow timing is carried out-of-band
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
* Bad, because it may break existing implementations or make them more complex in some cases

_Note:_ if the container has no internal timing, however the Flow has a rate and it can be assumed to have no gaps, the grain timestamp can still be calculated by computing its timestamp at the relevant rate from the beginning of the object, then mapping that into the Flow timeline using `ts_offset`.
In that case the media object timestamp for the first grain is `0:0`, so when the object was newly written and entirely used by a Flow Segment, `segment.ts_offset = segment.timerange.start`.
