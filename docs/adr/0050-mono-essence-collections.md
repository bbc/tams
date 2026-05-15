---
status: "proposed"
---
# Mono-Essence Collections

## Context and Problem Statement

In the discussion of [ADRXXXX Channel Mapping](./xxxx-channel-mapping.md) a mix of multi-essence Flows and mono-essence are used when considering multi-channel audio.

No clear guidance is given as to when one or the other should be used, and while the answer is obvious in some cases, where audio channels are involved the answers are less obvious.

## Considered Options

* Option 1: Collections always require multi-essence Flows and Sources
* Option 2: Require Multi-essence Flows for Collections unless describing multi-channel audio
* Option 3: Use Multi-essence vs Audio to indicate mapping direction (option C5 above)

## Decision Outcome

Chosen option: "{title of option 1}", because
{Justification, e.g., only option which resolves requirements, or comes out best (see below)}.

### Implementation

{Once the proposal has been implemented, add a link to the relevant PRs here}

## Pros and Cons of the Options

### Option 1: Collections always require multi-essence Flows and Sources

Add a requirement that `collects` is only valid for multi-essence Flows and Sources.

* Good, because it makes the correct one to use unambiguous
* Bad, because as discussed in ADRXXXX it is useful to be able to describe the channels of multi-channel audio separately

### Option 2: Require Multi-essence Flows for Collections unless describing multi-channel audio

Add documentation that `collects` is possible for Flows other than multi-essence, but only where the Flow that collects them together is intrinsically playable.
For example a stereo audio Flow having breakout Flows for the left and right channels would make sense.
However all 16 channels of SDI embedded audio, or multiple tracks of video would not make sense, and must be a mutli-essence Flow.

* Good, because it makes the correct one to less ambiguous
* Good, because it is likely to present players with Flows they can make sense of

### Option 3: Use Multi-essence vs Audio to indicate mapping direction (option C5 in ADRXXXX)

Use the multi-essence type to indicate that a reader should search the IDs in the Flow's `collected_by` list to find a Flow with essence (e.g. `container` property is set).
Use the mono-essence type (e.g. the Audio type) to mean searching the items the Flow `collects` to find a Flow with essence.

* Good, because it makes the correct one to use unambiguous
* Bad, because as disussed in ADRXXXX it breaks when there are multiple layers of collections
