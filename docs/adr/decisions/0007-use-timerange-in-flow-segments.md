---
status: "accepted"
---
# Use Timerange in Flow Segments

## Context and Problem Statement

The timerange of the media samples represented by the Flow Segment can either be represented as a timerange (currently `range`, but will be renamed to `timerange`) or a combination of `first_ts`, `last_ts` and `exclusive_last_ts`.

The original design used a `first_ts` and `last_ts` because the timeranges were required to be inclusive to support Flows with or without a media rate using the same representation.
The internal implementation also used the `first_ts` as a sort key.

The design was later changed to provide a choice between representations and to allow Flows with a media rate to use an exclusive timerange end.
A timerange with an exclusive end makes it easier to check for containment of a sample within the timerange given that audio and video samples for example have a duration.

## Considered Options

* Option 1: Allow either representation to be used
* Option 2: Only support the timerange representation

## Decision Outcome

Chosen option: Option 2: Only support the timerange representation, because it simplifies the API by removing duplication.

### Implementation

Implemented by [https://github.com/bbc/tams/pull/27](https://github.com/bbc/tams/pull/27)

## Pros and Cons of the Options

### Option 1: Allow either representation to be used

* Bad, because 2 representations for the timerange needs to be supported in the Flow Segment

### Option 2: Only support the timerange representation

* Good, because only 1 representation for the timerange needs to be supported in the Flow Segment
