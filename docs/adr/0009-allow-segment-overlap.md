---
status: "rejected"
---
# Allow Segments to Overlap

## Context and Problem Statement

Flows are defined to be immutable, so once a portion of the timeline has been written it cannot be changed.
However it is possible there are circumstances under which the segments themselves would need to change, or more generally to overlap, while containing the same content at each point in time.

## Considered Options

* Option 0: Reject the proposal and prohibit overlaps
* Option 1: Allow segments to overlap

## Decision Outcome

Chosen option: Rejecting the proposal, because the benefit of the widest possible support for media types and usage patterns is outweighed by the risk of reducing interoperability.

### Implementation

Implemented/Clarified in <https://github.com/bbc/tams/pull/32>

## Pros and Cons of the Options

### Option 1: Allow segments to overlap

Allow that segments may overlap (that is, have a `timerange` that intersects the `timerange` of another segment in the same Flow), with some defined mechanism to resolve how clients should handle that.

* Good, because it makes TAMS behave more like a media file container with the widest possible support for various media types and usage patterns.
* Good, because it avoids a requirement for multiple writers to the same Flow to produce the same segments.
* Good, because it allows for applications (and by extension their clients) to enforce restrictions relevant to that application, rather than making it part of the core API.
* Neutral, because it allows for gaps in segments to be filled in later (e.g. content that did not arrive at the ingester on time), however this can also be achieved by writing segments around the gap and the writing the missing segment, or by using copy-on-write to create a new Flow.
* Bad, because it creates more client complexity to deal with the overlaps, potentially reducing interoperability between clients.
* Bad, because it adds the potential to write broken Flows that aren't immutable, because segments have been overwritten.

## More Information

The BBC R&D TAMS team discussed this across a number of sessions, and eventually decided to reject the proposal.
It was felt that the benefit of the "widest possible support" was outweighed by the risk of reducing interoperability, and the ability for multiple TAMS API-compatible systems to interoperate is one of the core benefits of TAMS.
Furthermore it is not immediately clear that the ability to "fix" segments is useful in practice: if that part of the Flow has already been used then the "fix" may be editorially meaningful, and arguably should be viewed as a new Flow.
Parallels were drawn with Git, in which any change to any part of a commit changes the hash of the entire commit, and while Git has a mechanism to make "fixes" (rewriting history), that changes the identifiers used instead of changing their contents.

However, it may be that in future the ability to have overlapping segments becomes more important, at which point this proposal will be revisited, and a mechanism (e.g. a tag or a flag) could be added to indicate whether a Flow has overlapping segments or not, to allow clients to handle it appropriately.
