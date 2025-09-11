# Practical Application of the TAMS Content Model

## Abstract

This application note covers the basic principles of the Time Addressable Media Store's (TAMS) Content Model and explains how it can be applied to describe and manage media through some simple practical examples.
The terms `Source` and `Flow` are introduced and their meaning and usage are explored.
This short article will show you how `Flows` and `Sources` support flexible multi-format working and allow you to store, reference and synchronise sets of media elements at whatever level of granularity is required for your use cases.

## Content

### Describing and Managing Media with Flows and Sources

The Time Addressable Media Store uses strong, universally unique identifiers to manage and track media assets.
In most cases, these identifiers are coined when media is placed in the store (either by a file or stream ingest operation).

> ![NOTE:](../images/NOTE.svg) Ingest of media originating from an NMOS-compliant streaming device may persist the NMOS identifiers, since they conform to the same underlying model.
Future implementations of stream handling infrastructure may choose to embrace the TAMS content model more fully, adding identity and timing information that could be captured into the store, providing consistency between the streamed and stored domains.

Each media element is given a `Flow ID`, which is used to reference the content via the API.
The media Segments are indexed by time.
Once the media is in the store, it is never modified directly, and its `Flow ID` and relationship to the timeline never changes, ensuring that when you request a particular `Flow ID` and timerange via the API, you always get the same media Segments back.

`Sources` provide another layer of identity that groups together editorially-equivalent `Flows`, making it easy to find different representations of the same content.
For example, consider two `Flows`, comprising an H264 bitstream and a JPEG2000 bitstream respectively, representing the same sequence of pictures.
They share a `Source ID` and exist on the same timeline.
A request for the same timerange of either `Flow` will result in the same picture or sequence of pictures when decoded.
By extension, content can be referenced independent of its encoding by using the `Source IDs` directly, allowing clips and assembly edits to be described in purely editorial terms.

The TAMS content model provides a `collection` mechanism for grouping several mono-essence `Flow` entities together under a multi-essence `Flow ID`.
Mono-essence `Flows` can be referenced by any number of multi-essence `Flow collections`.

Storing the media elements independently affords more flexibility in cases where media elements regularly need to be manipulated separately, as it avoids the overhead of repeated unpacking and repacking.
As an alternative, multi-essence streams can be stored directly in muxed form if the flexibility of elemental media is not required.

> ![NOTE:](../images/NOTE.svg) TAMS use of `Sources` and `Flows` aligns with terminology used the Advanced Media Workflow Association's Networked Media Open Specifications.
TAMS extends some of the basic concepts to meet the needs of the practical applications it is designed to address.

Let's consider how the TAMS content model is used in practice through some simple examples.

### Simple Mono-essence Stream Ingest (stereo audio)

Ingest of a LPCM audio stream (for example an AES67 or SMPTE ST2110-30 stream) requires the creation of a new `Flow ID` to identify the sequence of Segments containing the audio samples, and a new `Source ID` as an editorial entity to support the linking of this media with other representations.

![Graphic showing ingest of an LPCM audio stream to create a TAMS Flow with its Source](./images/0001-multi-mono-essence-flows-sources-fig1.png)

> ![NOTE:](../images/NOTE.svg) By convention, the interleaved audio is treated as a single mono-essence `Flow`.
Implementers of media ingesters may choose to offer the option to split the interleave into several separate `Flows`.
If required, separate identifiers can be assigned to channels in an interleaved audio `Flow`, but that is beyond the scope of this application note.

### Creation of Proxy Representations

The audio Flow created in the previous example is encoded to produce a new AAC representation of the media.
A new `Flow ID` is coined to identify the new sequence of Segments.
The correspondence of the underlying samples to the timeline is inherited from the original media.
The new `Flow ID` is linked to the same `Source ID` as the original audio `Flow`.
Handling of alternative representations of video (and other types of media) follow the same pattern.

![Graphic showing creation of a proxy TAMS audio Flow from the LPCM representation, linked to the original via a common Source](./images/0001-multi-mono-essence-flows-sources-fig2.png)
> ![NOTE:](../images/NOTE.svg) The duration of the Segments in the derived `Flow` may differ due to technical constraints of the encoding algorithm or other reasons.
In this case, Segment timestamps will be remapped so the relationship between the timeline and the underlying media samples is preserved.

### Ingest of SRT Stream (video + stereo audio)

Stepping up to a stream containing both audio and video, packaged into a MPEG2 Transport Stream and encapsulated in SRT, three `Flow` entities are created on ingest: one for the video essence, one for the audio essence and a multi-essence `Flow` to record the association of the mono-essence `Flows` as an ingested stream.
The multi-essence `Flow` features a `collection` attribute that lists the `Flow IDs` in the set, each annotated with a string describing its role.

Technical metadata relating to the elementary streams is used to populate the corresponding mono-essence `Flow` properties.

For maximum flexibility, the video and audio essence is demuxed on ingest and stored separately under their respective mono-essence `Flow IDs`.
The synchronisation relationship between the elements is preserved through the use of a common time index for the set.

![Graphic showing ingest of an AV stream to create a set of TAMS Flows and Sources, stored as mono-essence](./images/0001-multi-mono-essence-flows-sources-fig3.png)

If your use case doesn't require this flexibility, it may be more convenient to store the multi-essence stream (in this case a Transport Stream) directly under the multi-essence `Flow` identifier, leaving the mono-essence `Flows` unpopulated, as shown below.

![Graphic showing ingest of an AV stream to create a set of TAMS Flows and Sources, stored as multi-essence](./images/0001-multi-mono-essence-flows-sources-fig4.png)

### Addition of Ancillary or Alternative Audio

`Flows` are logically independent and are associated with other `Flows` via the `collection` mechanism, so new `Flows` can be created to augment your assets at any time.
The synchronisation relationship between two or more `Flows` is encoded into their relationship to a common timeline.
As a result, adding ancillary or alternative audio to a set of media is as simple as creating the new media co-timed with the other items in the set, and introducing a new multi-essence `Flow` (and corresponding multi-essence `Source`) to define the augmented media `collection`.

![Graphic showing addition of audio description to the collection of TAMS Flows and Sources](./images/0001-multi-mono-essence-flows-sources-fig5.png)

> ![NOTE:](../images/NOTE.svg) It's technically permissible to collect together a mixture of mono- and multi-essence Flows into a higher-level multi-essence Flow.
However, creating multi-level hierarchies like this breeds complexity and will likely impact performance, so it's inadvisable in most cases.
It's generally better to reference the lowest-level mono-essence Flows individually in the multi-essence collection.

### Addition of Video Layers

Video layers or overlays can also be stored as separate `Flows`, synchronised using the same mechanism as in the audio example above.

![Graphic showing addition of audio description to the collection of TAMS Flows and Sources](./images/0001-multi-mono-essence-flows-sources-fig6.png)

Being able to reference these audio and video layers independently and bind them together in different combinations offers greater flexibility in downstream media workflows, and for future re-use of media assets.
