---
status: proposed
---
# Require Explicit Framerate

## Context and Problem Statement

In [#64](https://github.com/bbc/tams/pull/64) the set of required and optional parameters were audited, and during that process the behaviour of a video Flow without an (optional) `frame_rate` parameter was clarified, such that it describes:

> The fixed number of frames per second.
> If this parameter is unset, the frame_rate is either unknown or variable.

However subsequent feedback has indicated that handling the possibility of an unset frame rate remains confusing, and the matter should be revisited.
In particular, it should be considered whether the special case of Variable Frame Rate (VFR) content should be more explicitly called out in a Flow.

## Decision Drivers

* It is possible for a Video Flow to exist without a single specific frame rate: e.g. VFR content - however that requires more specialist handling by a reader
* Currently the same indication (no `frame_rate`) is used to indicate both VFR and the frame rate being unknown

## Considered Options

* Option 1: Retain the existing behaviour and description
* Option 2: Add a separate VFR flag, and use the schema to require either a frame_rate or that flag
* Option 2a: Further allow the possibility to not set a frame rate

## Decision Outcome

Option 2 (add a separate VFR flag) because it makes much clearer the presence of VFR content, and makes it easier for tools and users to detect it.
Additionally no known use case has been identified for unknown frame rates in video (Option 2a) - note that this does not apply to Data Flows, which can have data points at unspecified rates.

### Implementation

Implemented by <https://github.com/bbc/tams/pull/143>.

## Pros and Cons of the Options

### Option 1: Retain the existing behaviour and description

Retain the existing behaviour that `frame_rate` is optional, and if not set it is unknown or variable.

* Good, because it avoids a change to the specification
* Good, because it minimises the number of parameters and permutations available in the JSON body of a Flow
* Bad, because it "hides" the possibility of VFR content
* Bad, because it isn't clear that having an "unknown" frame-rate is meaningful

### Option 2: Add a separate VFR flag, and use the schema to require either a frame_rate or that flag

Add a new flag to a Video Flow's `frame_rate` called `vfr`.
Build the schema to make it mutually exclusive (a `oneOf` relationship) with the fractional variant, and require one or the other to be set.

* Good, because it makes the presence of VFR material very clear
* Good, because it enforces valid combinations (VFR or `frame_rate`, not both) using the schema
* Neutral, because it removes the possibility to create a non-VFR Video Flow without a frame rate, however it is not clear there are valid use cases for this
* Bad, because it makes the schema more complex and less human-readable (although validation tools and renderers should still cope well).

### Option 2a: Add a separate VFR flag but allow neither VFR nor `frame_rate` to be set

As above, add a new flag to a Video Flow `essence_parameters` called `vfr`.
However in this case both the rate and `vfr` are optional, allowing for the case of an unknown frame rate.
However enforcing that both are not set on the same Flow may have to either take place in the descriptive specification, or rely on a precedence mechanism (e.g. the fractional rate signals an average).

* Good, because it makes the presence of VFR material very clear
* Good, because it allows for VFR average frame rate to be signalled
* Bad, because invalid combinations have to be detected outside of the spec
* Neutral, because it enables the possibility to create a non-VFR Video Flow without a frame rate (e.g. an unknown frame rate), however it is not clear there are valid use cases for this
