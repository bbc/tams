---
status: proposed
---
# Source-level Edit

## Context and Problem Statement

TAMS provides a way to perform limited lightweight copy edits of Flows, where segments are reused in multiple places (see [the README.md](https://github.com/bbc/tams/tree/main?tab=readme-ov-file#flow-and-media-timelines)).
This opens up some interesting workflow possibilities, but comes with several notable limitations.

Firstly it works entirely in Flows, however the TAMS data model is intended to work with Sources for most editorial operations.
As it is, if a Source exists as a lightweight copy of another, every desired Flow has to be copied separately to create it in the store.
This could be a fairly expensive operation, especially because there's no way to bulk copy segments or parts of timerange.

Secondly it is quite a blunt instrument: the only operation that can be performed is a cut.
However new Flows can be created and re-used objects can coexist with new objects in the same store, so a tool could upload new objects and register new segments covering transitions and effects, while reusing objects otherwise.

Thirdly there's no mechanism for handling ancestry.
It is possible to find all of the Flows for which a given object is used, but only by exhaustively querying all Flows in the store to find where that ID is used.
An additional endpoint may be added in future to directly query where an object ID is used, and may be the subject of a future ADR.
Regardless, there is no way to reason about how a given Flow came in to existence: was it the originator of these segments, a copy or a copy-of-a-copy - for some applications (e.g. rights management) this can be quite important.

This ADR discusses some options for improving on these limitations.

## Considered Options

* Option 1: Provide an edit API in the store that allows more complex operations to be specified on Sources
* Option 2: Provide a limited API for simple cut operations on Sources
* Option 2a: Provide a limited API as in (Option 2), that prevents mixing Flow and Source operations
* Option 3: Provide additional Flow Segment API capability for more direct by-reference operations
* Option 4: Use another EDL format, outside the TAMS API.

## Decision Outcome

Chosen option: Options 3 and 4

In general the ability to easily re-use pieces of content and refer to them without duplicating essence is one of the strengths of TAMS, and opens up some interesting new workflows as a result.
EDL formats such as OpenTimelineIO are intended to be very powerful, but with that power comes complexity, which reduces the ease with which content may be re-used, meaning that Option 4 (another EDL format) alone doesn't make sense.
However using something like OpenTimelineIO is useful in some complex cases, so it makes sense to define a standard way to do so in TAMS.

Option 3 (expanded Flow Segment references) is chosen instead because it avoids prescribing an approach to selecting the relevant Flows from Source references.
While there are ways this could be approached (including ongoing discussion about "profiles" in Flows), the TAMS API is deliberately flexible in many places, and defining an approach by which implementations should decide the Flows to draw from when resolving references runs counter to this.
Option 2b (Source Timeline, without automatic de-referencing) is rejected because of the additional work required for a client to make use of the the Source timeline makes the feature less useful.

There is a gap between the simple Flow-centric approach in Option 3 and the complexity of EDL formats in Option 4.
If necessary, a layer could be placed over the top of TAMS, providing something more like Option 2 (Source timeline API endpoints) while constraining the implementation around the organisation's rules, e.g. for how Flows should be selected to construct new reference Flows.

### Implementation

{Once the proposal has been implemented, add a link to the relevant PRs here}

## Pros and Cons of the Options

### Option 1: Provide an edit API

Provide an API endpoint or set of endpoints that allow editorial operations to be described on Source timelines.
This could be thought of as a composition or edit decision API, allowing clients to write edits directly back to the store, describing how Sources get composed with transitions and effects.
Stores implementations or their clients could then render that composition on-the-fly, combining the underlying media while working by reference.

* Good, because it fully specifies complex compositions in a consistent way in the store.
* Good, because it allows for workflows that are fully edit-by-reference.
* Good, because it allows for referential workflows entirely using Sources.
* Bad, because it adds signficant additional complexity to store implementations or clients in order to implement the render process.
* Bad, because it creates *another* composition data format, when a large number already exist.

### Option 2: Provide a limited API for simple cut operations on Sources

Provide an API endpoint that allows Sources to use portions of the timerange of other Sources.
This would be equivalent to the existing object-reuse mechanism for Flows, while mitigating the shortcomings listed above.
The API would allow a client to specify that part of a Source timeline is drawn from another Source - see <https://github.com/bbc/tams/commit/82bd1be> for a possible implementation and examples.
This would allow for a cuts-based edit without compositing, however the Flows that represent these Sources could have new segments added to cover transitions.

For example, given Sources A and B, a new Source C could exist containing `SourceA@[0:0_9:0)`, then a 2 second gap, then `SourceB@[1:0_10:0)`.
When a new Flow C is created, additional segments could be created covering `[9:0_11:0)` (the 2 second gap) containing a dissolve between the relevant Flows A and B.
It's assumed in the example that attempts to reference a Source that is already a reference will look through and reference against the underlying Source instead, providing a way to identify the original Source as well.

Where suitable Flows exist of those Sources, store implementations could "invent" the relevant segments themselves.
In the example above, given a Flow A and B, the store could respond a request for `GET /flows/<flowC>/segments?timerange=[5:0_6:0)` with the Flow Segments for Flow A at `[5:0_6:0)`.
However this is much more complex in cases where more than one Flow exists of each Source: how would a store identify the correct Flow in the original Source that should be mapped to the new Flow in the new Source.

* Good, because it allows for limited edit-by-reference workflows in the store.
* Good, because it provides a way to edit operations (albeit limited ones) using Sources.
* Good, because it allows for more efficient copies: a timerange can be copied into another Source without needing to create large numbers of new segment entries.
* Good, because it provides a way to handle more complex edit/composition operations by writing new segments.
* Good, because at read time the references are transparent to a client: the store can read-through them.
* Good, because it's clear which Source a new Source originated from.
* Neutral, because it's not clear how Flows should come into existence from reference-based Sources (although some kind of profile mechanism could be introduced for matching compatible Flows).
* Bad, because some areas of a Flow timeline could originate due to a Source-level reference, and some due to new segments being created directly: care would need to be taken if the same point on a Source timeline is specified in two different ways.
* Bad, because it adds additional complexity to the API, and would likely introduce a breaking change.

### Option 2a: Provide a limited API as in (Option 2), that prevents mixing Flow and Source operations

As above, however if the Source-level edit endpoint is used on a given Source, Flow Segments cannot be created for the Flows.
Instead the Source, and all the Flows that represent it, must be fully described using references to other Sources.
In the case where new segments need to be written (e.g. to cover a transition) a new Flow and Source can be created as the "transition layer", which can then be composed into a new Source.

Building on the example above, instead we now have Flow/Source pairs A, B and D, where D contains only the rendered dissolve between A and B.
The resulting Flow/Source pair C contains `SourceA@[0:0_9:0)`, `SourceD@[9:0_11:0)`, `SourceB@[1:0_10:0)`.

This option has the same list of pros and cons above, expect the following item is mitigated and removed:

> Bad, because some areas of a Flow timeline could originate due to a Source-level reference, and some due to new segments being created directly: care would need to be taken if the same point on a Source timeline is specified in two different ways.

### Option 2b: Provide a limited API as in (Option 2), that only works on Sources

As above, however store implementations cannot "invent" the relevant segments: they merely provide detail of the Source timeline and leave the rest to the client.

This option has the same list of pros and cons as Option 2, however the following benefit is removed:
> Good, because at read time the references are transparent to a client: the store can read-through them.

And the following drawback is added:
> Bad, because clients have to do significant additional work to make use of a Source timeline (identifying, de-referencing and re-mapping the relevant Flows).

### Option 3: Provide additional Flow Segment API capability for more direct by-reference operations

To avoid the Flow mapping complexity introduced by Option 2/2a, another approach would be to continue working directly with Flows, but reduce the friction to creating copies of all existing Flows.
Instead of having to create a new Flow Segment for every copied segment in the original Flow, this option proposes an additional form of "reference" Flow Segment.

The references could take a form such as:

```json
[
    {
        "reference": {
            "flow_id": "flow-a-id",
            "timerange": "[0:0_9:0)"
        },
        "timerange": "[0:0_9:0)",
        "ts_offset": "0:0",
    },
    {
        "reference": {
            "flow_id": "flow-d-id",
            "timerange": "[0:0_2:0)"
        },
        "timerange": "[9:0_11:0)",
        "ts_offset": "0:0",
    },
    {
        "reference": {
            "flow_id": "flow-c-id",
            "timerange": "[1:0_10:0)"
        },
        "timerange": "[11:0_20:0]",
        "ts_offset": "10:0",
    }
]
```

It would make sense to have `POST /flows/<flowid>/segments` accept one of these reference objects as an alternative to supplying an `object_id` directly.
However on read it would make sense to automatically de-reference and return standard Flow Segments drawn from the underlying Flow.
An additional query parameter could be added, such that `GET /flows/<flowid>/segments?dereference=false` returns the references directly, for workflows that need that information.

While this doesn't allow working directly with Sources, it might make propagating a lightweight copy across all the Flows of a Source much more efficient (providing there are a relatively small number of edit points).

* Good, because it allows for limited edit-by-reference workflows in the store.
* Good, because it allows for more efficient copies: a timerange can be copied into another Flow without needing to create large numbers of new segment entries.
* Good, because it provides a way to handle more complex edit/composition operations by writing new segments as in Option 2.
* Good, because it's clear which Flow a new Flow originated from.
* Neutral, because it avoids a problem with which Flows come into existence, by moving it to the client's responsibility.
* Bad, because it still requires working with Flows rather than Sources.

### Option 4: Use another EDL format, outside the TAMS API

Instead of providing a more complete mechanism for lightweight edit in the TAMS API, another format could be recommended and used with references to material in a TAMS instance.
For example [OpenTimelineIO](https://github.com/AcademySoftwareFoundation/OpenTimelineIO) (or OTIO) is deliberately flexible to how the underlying media is referenced: intended to make relinking compositions as they move between systems easier, but the same approach could be applied to reference media in a TAMS store.

This would likely take the form of an Application Note, suggesting how OTIO might be used with TAMS to reference content either as a URL to a store, or a `MissingReference` with the ID in metadata.
An example is provided below as an illustration.

Additional capabilities could be built on top of the combination of TAMS and OTIO, for example rendering an OTIO composition using lightweight Flow copies (and new objects for the transitions as in the examples above), or generating OTIO as part of a metadata-driven editorial workflow.

* Good, because it allows for complex compositions in a consistent way.
* Good, because it moves a significant amount of complexity into an existing technology.
* Good, because OTIO has growing support in other tools (e.g. NLEs).
* Good, because the flexible plugin model in OTIO (e.g. Media Linkers) could be used to bridge into other tools: for example fetching Flows as a file locally for an NLE without direct TAMS support.
* Neutral, because it requires incorporating an additional tech stack.
* Bad, because OTIO might be overkill for simple operations such as basic clipping.

## Appendix: OpenTimelineIO TAMS References

This appendix illustrates how TAMS references might work in OpenTimelineIO compositions.

### URL Form

This form uses an `ExternalReference` to a URL in a TAMS instance.

Notice that the URL has a prefix `tamss://` (for "TAMS Secure" - `tams://` would also work for HTTP).
In addition the `start_time` and `duration` in the `available_range` are Flow timestamps with nanosecond precision,
referring to the timerange over which the Flow is available.
The `source_range` also has a `start_time` as a nanosecond timestamp within the same Flow.

```json
{
    "OTIO_SCHEMA": "Clip.2",
    "metadata": {},
    "name": "camera-one.ts",
    "source_range": {
        "OTIO_SCHEMA": "TimeRange.1",
        "duration": {
            "OTIO_SCHEMA": "RationalTime.1",
            "rate": 50.0,
            "value": 111.0
        },
        "start_time": {
            "OTIO_SCHEMA": "RationalTime.1",
            "rate": 1000000000.0,
            "value": 1723124225400000000.0
        }
    },
    "effects": [],
    "markers": [],
    "enabled": true,
    "media_references": {
        "DEFAULT_MEDIA": {
            "OTIO_SCHEMA": "ExternalReference.1",
            "metadata": {},
            "name": "camera-one.ts",
            "available_range": {
                "OTIO_SCHEMA": "TimeRange.1",
                "duration": {
                    "OTIO_SCHEMA": "RationalTime.1",
                    "rate": 1000000000.0,
                    "value": 372100000000.0
                },
                "start_time": {
                    "OTIO_SCHEMA": "RationalTime.1",
                    "rate": 1000000000.0,
                    "value": 1723124086620000000
                }
            },
            "available_image_bounds": null,
            "target_url": "tamss://tams.example.com/flows/9bb414a5-862c-494f-86ce-8e2720ecc315"
        }
    },
    "active_media_reference_key": "DEFAULT_MEDIA"
}
```

### Reference Form

This form uses metadata to reference a Flow (or potentially Source) ID.

```json
"media_references": {
    "DEFAULT_MEDIA": {
        "OTIO_SCHEMA": "ExternalReference.1",
        "metadata": {
            "bbc.github.io/tams": {
                "flow_id": "9bb414a5-862c-494f-86ce-8e2720ecc315",
                "available_range_offset": "0:0"
            }
        },
        "name": "camera-one.ts",
        "available_range": {
            "OTIO_SCHEMA": "TimeRange.1",
            "duration": {
                "OTIO_SCHEMA": "RationalTime.1",
                "rate": 1000000000.0,
                "value": 372100000000.0
            },
            "start_time": {
                "OTIO_SCHEMA": "RationalTime.1",
                "rate": 1000000000.0,
                "value": 1723124086620000000
            }
        },
        "available_image_bounds": null,
        "target_url": "tamss://tams.example.com/flows/9bb414a5-862c-494f-86ce-8e2720ecc315"
    }
}
```

Note the addition of an `available_range_offset` that describes how the `available_range` here maps onto the Flow timeline, much as `ts_offset` remaps media essence timing to Flow timing.
