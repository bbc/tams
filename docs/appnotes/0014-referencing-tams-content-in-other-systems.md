# 0014: Referencing TAMS content in other systems

## Abstract

Many workflows require that TAMS content be referenced in other systems or operations, or example linking it to an asset in a MAM, using it to describe an edit composition or integrating it with signals in the live domain.
This Application Note describes a number of common reference formats to describe these use cases.

This is intended to be a working document, and as new use cases are built out, new formats may be added.

### URI References

Content in a TAMS instance can be referred to by URI, for example `https://tams.example.com/flows/f87f7f32-a34d-4a6f-b085-a5ee49b4b2f8`, although in some cases (where the presence of a TAMS API is otherwise not indicated), it may be useful to refer to the "pseudo-protocol" `tams://`.

In some cases a client may choose to ignore the location part of the URI, and parse it to identify the type (e.g. Flow or Source) and UUID.
These could be applied to another TAMS interface known to the client: for example a local cache or a store interface aggregator.
This is made possible by Flows and Sources having a unique identifier, which should always point to that particular Flow or Source without colliding.

#### Referring directly to a Flow

```text
https://tams.example.com/flows/f87f7f32-a34d-4a6f-b085-a5ee49b4b2f8
```

#### Referring directly to a Source

When referring to an "asset" that contains, for example, video and audio (e.g. attaching a clip in a MAM to an underlying TAMS concept), the reference should point to the relevant multi-essence Source.
Clients will need to use the Source's collection to select the relevant Sources, and from there identify suitable Flows.

This should be the preferred approach when referring to content, unless it is necessary to point to a specific Flow.

```text
https://tams.example.com/sources/7abe4d59-7d1c-432d-ba2a-6180e12137cc
```

#### Referring to a specific TimeRange of a Flow

To refer to a specific TimeRange of a Flow, use the relevant Flow Segment endpoint directly.

```text
https://tams.example.com/flows/f87f7f32-a34d-4a6f-b085-a5ee49b4b2f8/segments?timerange=[100:0_200:0)
```

#### Referring to a specific TimeRange of a Source

However there is no direct API concept to refer to a specific TimeRange of a Source.
Instead, this form can be used, and a client can map it accordingly after traversing the Source/Flow graph.

```text
https://tams.example.com/sources/7abe4d59-7d1c-432d-ba2a-6180e12137cc?timerange=[100:0_200:0)
```

## JSON Object References

In places where a JSON object is required to refer to a Flow or Source (for example [OpenTimelineIO compositions](./0015-using-tams-in-opentimelineio.md)), it can contain keys directly referring to Source IDs (or, if necessary, Flow IDs using a `flow_id` key).
The example below shows a JSON object with an identifying namespace (as recommended by OpenTimelineIO).
A "hint URL" could also be included, suggesting the location of a store at which the Source can be accessed.
Alternatively the URI form above can be used.

```json
"bbc.github.io/tams": {
    "source_id": "9bb414a5-862c-494f-86ce-8e2720ecc315",
    "hint_url": "https://tams.example.com/v5.1/"
}
```

## String References

When referring to a TAMS Object as a string, the URI reference style above may be used, and will make sense in many cases.

If a clear need arises, alternative forms such as URNs or [tag URIs](https://www.rfc-editor.org/rfc/rfc4151.html) will be added via the ADR process.

## Live Signal Domain

The TAMS identity model is deliberately aligned with that of [AMWA NMOS MS-04](https://specs.amwa.tv/ms-04/releases/v1.0.0/docs/2.1._Summary_and_Definitions.html), to facilitate alignment of fast-turnaround, live and file-based workflows.
It is expected that when content is ingested into TAMS in an NMOS environment, the Flow and Source IDs and internal timing of that content is preserved and can be considered as part of a unified control system.

When content is played out into a live signal environment, it is likely to be time-shifted to align with other content, which requires that a new Source and Flow ID be assigned (as described in the [MS-04 Playout Server example](https://specs.amwa.tv/ms-04/releases/v1.0.0/docs/3.2._Composite_Media_Operations.html#playout-server)).
In that case, it may be useful to create that new Flow in the store as well, by using the [Flow reference mechanism](../../README.md#flow-and-media-timelines) to create it as a lightweight copy.
This would allow what happened in the live domain to be captured, and then referenced after-the-fact using TAMS as well.

In non-NMOS environments (e.g.) SDI, it is desirable to carry identity and timing metadata, however no process for doing so has been proposed at present.
