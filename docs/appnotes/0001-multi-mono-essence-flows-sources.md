# Practical Application of the TAMS Content Model

## Abstract

This application note covers the basic principles of the Time Addressable Media Store's (TAMS) Content Model and explains how it can be applied to describe and manage media through some simple practical examples.
The terms `Source` and `Flow` are introduced and their meaning and usage are explored.
This short article will show you how `Flows` and `Sources` support flexible multi-format working and allow you to store, reference and synchronise sets of media elements at whatever level of granularity is required for your use cases.

## Content

### Describing and Managing Media with Flows and Sources

The Time Addressable Media Store uses strong, universally unique identifiers to manage and track media assets.
In most cases, these identifiers are coined when media is placed in the store (either by a file or stream ingest operation).

> [!NOTE]
> Ingest of media originating from an NMOS-compliant streaming device may persist the [NMOS identifiers](https://specs.amwa.tv/ms-04/releases/v1.0.0/docs/2.1._Summary_and_Definitions.html), since they conform to the same underlying model.
Future implementations of stream handling infrastructure may choose to embrace the TAMS content model more fully, adding identity and timing information that could be captured into the store, providing consistency between the streamed and stored domains.

Each media element is given a `Flow ID`, which is used to reference the content via the API.
This media is typically chunked and stored as Media Objects.
These Media Objects are typically short (on the order of seconds) and independently decodable to allow for efficient random access of content.
Media Objects are mapped to a Flow's timeline via Flow Segments.

Once media is in the store, it is considered immutable and never modified directly.
A Flow's `Flow ID`, its Flow Segments, and their relationship to the Flow's timeline never changes.
This ensures that when you request a particular `Flow ID` and timerange via the API, you always get the same media back.

The length of Media Objects is dependent on limitations of codecs and their configuration (such as GOP sizes) along with a trade-off between number of requests to upload/download content, cost, and granularity.
Multiple Flow Segments, in the same or different Flows, may reference the same Media Object.
Flow Segments may reference partial Media Objects, allowing for frame/sample accuracy.
This is particularly useful when re-using existing Media Objects in so-called edit-by-reference workflows.

`Sources` provide another layer of identity that groups together editorially-equivalent `Flows`, making it easy to find different representations of the same content.
For example, consider two `Flows`, comprising an H264 bitstream and a JPEG2000 bitstream respectively, representing the same sequence of pictures.
They share a `Source ID` and exist on the same timeline.
A request for the same timerange of either `Flow` will result in the same picture or sequence of pictures when decoded.
By extension, content can be referenced independent of its encoding by using the `Source IDs` directly, allowing clips and assembly edits to be described in purely editorial terms.

The TAMS content model provides a `collection` mechanism for grouping several mono-essence `Flow` entities together under a multi-essence `Flow` (Multi-Flow).
Mono-essence `Flows` can be referenced by any number of Multi-Flows via their `flow_collection` attribute.
Counterpart `source_collection` attribute also exist against `Sources` and are created by TAMS services automatically based on their Flow equivalents.

It is considered best practice to deal with media as Sources wherever possible, particularly when presenting that media to human users.
Systems are often better placed to decide which technical representation (i.e. Flow) is most appropriate for their use than other systems or human users.
There will also typically be fewer Sources available than Flows, resulting in shorter listings in UIs etc.
These listings may, in some use cases, be further filtered to just Multi-Sources which collect related media.
It may, be appropriate to deal in Flows directly in cases where specific technical representations are important.
For example, when passing Flows to a file-export service.

Storing the media elements independently affords more flexibility in cases where media elements regularly need to be manipulated separately, as it avoids the overhead of repeated unpacking and repacking.
For example, a transcription service would need access to audio, but not video.
And generation of video proxies would not need access to audio.
Additionally, it avoids the need to create separate multiplexed streams for all combinations of audio and video qualities.
This saves on resources.

As an alternative, multi-essence streams can be stored directly in muxed form if the flexibility of elemental media is not required.
This may be of particular use where the original stream must be retained for compliance reasons.

> [!NOTE]
> TAMS use of `Sources` and `Flows` aligns with terminology used the Advanced Media Workflow Association's Networked Media Open Specifications.
TAMS extends some of the basic concepts to meet the needs of the practical applications it is designed to address.

Let's consider how the TAMS content model is used in practice through some simple examples.

### Simple Mono-essence Stream Ingest (stereo audio)

Ingest of a LPCM audio stream (for example an AES67 or SMPTE ST2110-30 stream) requires the creation of a new `Flow ID` to identify the sequence of Segments containing the audio samples, and a new `Source ID` as an editorial entity to support the linking of this media with other representations.
The chunked media is stored as Media Objects and mapped onto the Flow's timeline via Flow Segments.

> [!NOTE]
> Other examples in this Application Note omit Media Objects for brevity

```mermaid
block-beta
columns 8
    space:4
    dummy1[" "]
    space:2
    dummy2[" "]
    dummy1 -- "Time" --> dummy2
    style dummy1 fill:none, stroke:transparent;
    style dummy2 fill:none, stroke:transparent;

    a_s["Source \n Audio \n (BBC Proms R3 Mix)"]
    space:1
    a_f["Flow \n Audio \n LPCM Stereo \n (BBC Proms R3 Mix - High Quality)"]
    space:1
    a_fs_1["Segment \n (LPCM)"]
    a_fs_2["Segment \n (LPCM)"]
    a_fs_3["Segment \n (LPCM)"]
    a_fs_4["Segment \n (LPCM)"]
    a_f -- "Represents" --> a_s
    a_f --- a_fs_1

    space:8

    space:4
    a_mo_1["Media Object \n (LPCM)"]
    a_mo_2["Media Object \n (LPCM)"]
    a_mo_3["Media Object \n (LPCM)"]
    a_mo_4["Media Object \n (LPCM)"]

    a_fs_1 -- "References" --> a_mo_1
    a_fs_2 -- "References" --> a_mo_2
    a_fs_3 -- "References" --> a_mo_3
    a_fs_4 -- "References" --> a_mo_4

    classDef source fill:#00BF7D,color:#000
    classDef flow fill:#0073E6,color:#FFF
    classDef segment fill:#5928ED,color:#FFF
    classDef object fill:#00B4C5,color:#000

    class a_s source
    class a_f flow
    class a_fs_1,a_fs_2,a_fs_3,a_fs_4 segment
    class a_mo_1,a_mo_2,a_mo_3,a_mo_4 object
```

> [!NOTE]
> By convention, the interleaved audio is treated as a single mono-essence `Flow`.
Implementers of media ingesters may choose to offer the option to split the interleave into several separate `Flows`.
If required, separate identifiers can be assigned to channels in an interleaved audio `Flow`, but that is beyond the scope of this application note.

### Creation of Proxy Representations

The audio Flow created in the previous example is encoded to produce a new AAC representation of the media.
A new `Flow ID` is coined to identify the new sequence of Segments.
The correspondence of the underlying samples to the timeline is inherited from the original media.
The new `Flow ID` is linked to the same `Source ID` as the original audio `Flow`.
Handling of alternative representations of video (and other types of media) follow the same pattern.

```mermaid
block-beta
columns 8
    space:4
    dummy1[" "]
    space:2
    dummy2[" "]
    dummy1 -- "Time" --> dummy2
    style dummy1 fill:none, stroke:transparent
    style dummy2 fill:none, stroke:transparent

    space:2
    a_f_a["Flow \n Audio \n LPCM Stereo \n (BBC Proms R3 Mix - High Quality)"]
    space:1
    a_fs_a1["Segment \n (LPCM)"]
    a_fs_a2["Segment \n (LPCM)"]
    a_fs_a3["Segment \n (LPCM)"]
    a_fs_a4["Segment \n (LPCM)"]
    a_f_a -- "Represents" --> a_s
    a_f_a --- a_fs_a1

    a_s["Source \n Audio \n (BBC Proms R3 Mix)"]
    space:7

    space:2
    a_f_b["Flow \n Audio \n AAC Stereo \n (BBC Proms R3 Mix - Compressed)"]
    space:1
    a_fs_b1["Segment \n (AAC)"]
    a_fs_b2["Segment \n (AAC)"]
    a_fs_b3["Segment \n (AAC)"]
    a_fs_b4["Segment \n (AAC)"]
    a_f_b -- "Represents" --> a_s
    a_f_b --- a_fs_b1

    classDef source fill:#00BF7D,color:#000
    classDef flow fill:#0073E6,color:#FFF
    classDef segment fill:#5928ED,color:#FFF

    class a_s source
    class a_f_a,a_f_b flow
    class a_fs_a1,a_fs_a2,a_fs_a3,a_fs_a4,a_fs_b1,a_fs_b2,a_fs_b3,a_fs_b4 segment
```

> [!NOTE]
> The duration of the Segments in the derived `Flow` may differ due to technical constraints of the encoding algorithm or other reasons.
In this case, Segment timestamps will be remapped so the relationship between the timeline and the underlying media samples is preserved.

### Ingest of SRT Stream (video + stereo audio)

Stepping up to a stream containing both audio and video, packaged into a MPEG2 Transport Stream and encapsulated in SRT, three `Flow` entities are created on ingest: one for the video essence, one for the audio essence and a Multi-Flow to record the association of the mono-essence `Flows` as an ingested stream.
The Multi-Flow features a `collection` attribute that lists the `Flow IDs` in the set, each annotated with a string describing its role.

Technical metadata relating to the elementary streams is used to populate the corresponding mono-essence `Flow` properties.

For maximum flexibility, the video and audio essence is demuxed on ingest and stored separately under their respective mono-essence `Flow IDs`.
The synchronisation relationship between the elements is preserved through the use of a common time index for the set.

```mermaid
block-beta
columns 11
    s_m["Source \n Multi-essence \n (Original feed)"]
    space:3
    f_m["Flow \n Multi-essence \n (Original feed)"]
    space:6
    f_m -- "Represents" --> s_m

    space:11

    space:7
    time_dummy_1[" "]
    space:2
    time_dummy_2[" "]
    time_dummy_1 -- "Time" --> time_dummy_2
    style time_dummy_1 fill:none, stroke:transparent;
    style time_dummy_2 fill:none, stroke:transparent;

    space:1
    s_v["Source \n Video \n (Main)"]
    space:3
    f_v["Flow \n Video \n H264 \n (Main)"]
    space:1
    fs_v_1["Video \n Segment"]
    fs_v_2["Video \n Segment"]
    fs_v_3["Video \n Segment"]
    fs_v_4["Video \n Segment"]
    f_v -- "Represents" --> s_v
    f_v --- fs_v_1

    s_a["Source \n Audio \n (Production Sound)"]
    space:3
    f_a["Flow \n Audio \n AAC \n (Production Sound)"]
    space:2
    fs_a_1["Audio \n Segment"]
    fs_a_2["Audio \n Segment"]
    fs_a_3["Audio \n Segment"]
    fs_a_4["Audio \n Segment"]
    f_a -- "Represents" --> s_a
    f_a --- fs_a_1

    s_m -- "Collects" --> s_v
    s_m -- "Collects" --> s_a

    f_m -- "Collects" --> f_v
    f_m -- "Collects" --> f_a

    classDef source fill:#00BF7D,color:#000
    classDef flow fill:#0073E6,color:#FFF
    classDef segment fill:#5928ED,color:#FFF

    class s_m,s_a,s_v source
    class f_m,f_a,f_v flow
    class fs_a_1,fs_a_2,fs_a_3,fs_a_4,fs_v_1,fs_v_2,fs_v_3,fs_v_4 segment
```

If your use case doesn't require this flexibility, it may be more convenient to store the multi-essence stream (in this case a Transport Stream) as muxed Media Objects, with Flow Segments being populated directly against the Multi-Flow, leaving the mono-essence Flows unpopulated, as shown below.

> [!NOTE]
> Unpopulated mono-essence `Flows` collected by populated Multi-Flows are often still useful for conveying the technical properties of the tracks within the multiplexed stream of the Multi-Flow.
This aids consuming clients in identifying media they are compatible with.

```mermaid
block-beta
columns 11
    space:7
    time_dummy_1[" "]
    space:2
    time_dummy_2[" "]
    time_dummy_1 -- "Time" --> time_dummy_2
    style time_dummy_1 fill:none, stroke:transparent;
    style time_dummy_2 fill:none, stroke:transparent;

    s_m["Source \n Multi-essence \n (Original feed)"]
    space:3
    f_m["Flow \n Multi-essence \n (Original feed)"]
    space:2
    fs_m_1["Muxed \n Segment"]
    fs_m_2["Muxed \n Segment"]
    fs_m_3["Muxed \n Segment"]
    fs_m_4["Muxed \n Segment"]
    f_m -- "Represents" --> s_m
    f_m --- fs_m_1

    space:11

    space:11

    space:1
    s_v["Source \n Video \n (Main)"]
    space:3
    f_v["Flow \n Video \n H264 \n (Main)"]
    space:5
    f_v -- "Represents" --> s_v

    s_a["Source \n Audio \n (Production Sound)"]
    space:3
    f_a["Flow \n Audio \n AAC \n (Production Sound)"]
    space:6
    f_a -- "Represents" --> s_a

    s_m -- "Collects" --> s_v
    s_m -- "Collects" --> s_a

    f_m -- "Collects" --> f_v
    f_m -- "Collects" --> f_a

    classDef source fill:#00BF7D,color:#000
    classDef flow fill:#0073E6,color:#FFF
    classDef segment fill:#5928ED,color:#FFF

    class s_m,s_a,s_v source
    class f_m,f_a,f_v flow
    class fs_m_1,fs_m_2,fs_m_3,fs_m_4 segment
```

### Quality Ladder

In many cases, a "quality ladder" of representations may be provided to suit different bandwidths, display resolutions, and quality requirements etc.
The general principle in TAMS is that the media required should be communicated at the Source level where possible.
It should be up to the client to decide the Flows required automatically, where possible, as it will often have more data regarding the requirements and resources available than the user.
As the number of renditions increases, the number of possible combinations also increases.
For this reason, it recommended to only create Multi-Flows where they provide value to the system.
For example the initial Flows collections that will, by extension, create the Source collections that may be used to identify different renditions.
Or the creation of a specific Flow collection to pass to render server.

```mermaid
block-beta
columns 14
    space:1
    s_m["Source \n Multi-essence \n (Original feed)"]
    space:5
    f_m_a["Flow \n Multi-essence \n (Original feed) \n (HQ Audio + UHD)"]
    space:6
    f_m_a -- "Represents" --> s_m

    space:14

    space:14

    space:10
    time_dummy_1[" "]
    space:2
    time_dummy_2[" "]
    time_dummy_1 -- "Time" --> time_dummy_2
    style time_dummy_1 fill:none, stroke:transparent;
    style time_dummy_2 fill:none, stroke:transparent;

    s_a["Source \n Audio \n (Production Sound)"]
    space:7
    f_a_a["Flow \n Audio \n AAC \n (High Quality Sound)"]
    space:1
    fs_a_a1["HQ Audio \n Segment"]
    fs_a_a2["HQ Audio \n Segment"]
    fs_a_a3["HQ Audio \n Segment"]
    fs_a_a4["HQ Audio \n Segment"]
    f_a_a -- "Represents" --> s_a
    f_a_a --- fs_a_a1

    space:7
    f_a_b["Flow \n Audio \n AAC \n (Low Quality Sound)"]
    space:2
    fs_a_b1["LQ Audio \n Segment"]
    fs_a_b2["LQ Audio \n Segment"]
    fs_a_b3["LQ Audio \n Segment"]
    fs_a_b4["LQ Audio \n Segment"]
    f_a_b -- "Represents" --> s_a
    f_a_b --- fs_a_b1

    space:1
    s_v["Source \n Video \n (Main)"]
    space:4
    f_v_a["Flow \n Video \n 2160p \n (Main - UHD)"]
    space:3
    fs_v_a1["UHD Video \n Segment"]
    fs_v_a2["UHD Video \n Segment"]
    fs_v_a3["UHD Video \n Segment"]
    fs_v_a4["UHD Video \n Segment"]
    f_v_a -- "Represents" --> s_v
    f_v_a --- fs_v_a1

    space:5
    f_v_b["Flow \n Video \n 1080p \n (Main - HD)"]
    space:4
    fs_v_b1["HD Video \n Segment"]
    fs_v_b2["HD Video \n Segment"]
    fs_v_b3["HD Video \n Segment"]
    fs_v_b4["HD Video \n Segment"]
    f_v_b -- "Represents" --> s_v
    f_v_b --- fs_v_b1

    space:4
    f_v_c["Flow \n Video \n 480p \n (Main - SD)"]
    space:5
    fs_v_c1["SD Video \n Segment"]
    fs_v_c2["SD Video \n Segment"]
    fs_v_c3["SD Video \n Segment"]
    fs_v_c4["SD Video \n Segment"]
    f_v_c -- "Represents" --> s_v
    f_v_c --- fs_v_c1

    s_m -- "Collects" --> s_v
    s_m -- "Collects" --> s_a

    f_m_a -- "Collects" --> f_a_a
    f_m_a -- "Collects" --> f_v_a

    classDef source fill:#00BF7D,color:#000
    classDef flow fill:#0073E6,color:#FFF
    classDef segment fill:#5928ED,color:#FFF

    class s_m,s_a,s_v source
    class f_m_a,f_a_a,f_a_b,f_v_a,f_v_b,f_v_c flow
    class fs_a_a1,fs_a_a2,fs_a_a3,fs_a_a4,fs_a_b1,fs_a_b2,fs_a_b3,fs_a_b4,fs_v_a1,fs_v_a2,fs_v_a3,fs_v_a4,fs_v_b1,fs_v_b2,fs_v_b3,fs_v_b4,fs_v_c1,fs_v_c2,fs_v_c3,fs_v_c4 segment
```

> [!CAUTION]
> The following diagram is an anti-pattern that should be avoided

The following diagram demonstrates the proliferation of Flows, and exponential complexity that arises from representing all possible combinations of renditions as separate Multi-Flows.

```mermaid
block-beta
columns 14
    space:1
    s_m["Source \n Multi-essence \n (Original feed)"]
    space:6
    f_m_a["Flow \n Multi-essence \n (Original feed) \n (HQ Audio + UHD)"]
    space:5
    f_m_a -- "Represents" --> s_m

    space:7
    f_m_b["Flow \n Multi-essence \n (HQ Audio + HD)"]
    space:6
    f_m_b -- "Represents" --> s_m

    space:6
    f_m_c["Flow \n Multi-essence \n (HQ Audio + SD)"]
    space:7
    f_m_c -- "Represents" --> s_m

    space:5
    f_m_d["Flow \n Multi-essence \n (LQ Audio + UHD)"]
    space:8
    f_m_d -- "Represents" --> s_m

    space:4
    f_m_e["Flow \n Multi-essence \n (LQ Audio + HD)"]
    space:9
    f_m_e -- "Represents" --> s_m

    space:3
    f_m_f["Flow \n Multi-essence \n (LQ Audio + SD)"]
    space:10
    f_m_f -- "Represents" --> s_m

    space:14

    space:14

    space:14

    space:10
    time_dummy_1[" "]
    space:2
    time_dummy_2[" "]
    time_dummy_1 -- "Time" --> time_dummy_2
    style time_dummy_1 fill:none, stroke:transparent;
    style time_dummy_2 fill:none, stroke:transparent;

    s_a["Source \n Audio \n (Production Sound)"]
    space:7
    f_a_a["Flow \n Audio \n AAC \n (High Quality Sound)"]
    space:1
    fs_a_a1["HQ Audio \n Segment"]
    fs_a_a2["HQ Audio \n Segment"]
    fs_a_a3["HQ Audio \n Segment"]
    fs_a_a4["HQ Audio \n Segment"]
    f_a_a -- "Represents" --> s_a
    f_a_a --- fs_a_a1

    space:7
    f_a_b["Flow \n Audio \n AAC \n (Low Quality Sound)"]
    space:2
    fs_a_b1["LQ Audio \n Segment"]
    fs_a_b2["LQ Audio \n Segment"]
    fs_a_b3["LQ Audio \n Segment"]
    fs_a_b4["LQ Audio \n Segment"]
    f_a_b -- "Represents" --> s_a
    f_a_b --- fs_a_b1

    space:1
    s_v["Source \n Video \n (Main)"]
    space:4
    f_v_a["Flow \n Video \n 2160p \n (Main - UHD)"]
    space:3
    fs_v_a1["UHD Video \n Segment"]
    fs_v_a2["UHD Video \n Segment"]
    fs_v_a3["UHD Video \n Segment"]
    fs_v_a4["UHD Video \n Segment"]
    f_v_a -- "Represents" --> s_v
    f_v_a --- fs_v_a1

    space:5
    f_v_b["Flow \n Video \n 1080p \n (Main - HD)"]
    space:4
    fs_v_b1["HD Video \n Segment"]
    fs_v_b2["HD Video \n Segment"]
    fs_v_b3["HD Video \n Segment"]
    fs_v_b4["HD Video \n Segment"]
    f_v_b -- "Represents" --> s_v
    f_v_b --- fs_v_b1

    space:4
    f_v_c["Flow \n Video \n 480p \n (Main - SD)"]
    space:5
    fs_v_c1["SD Video \n Segment"]
    fs_v_c2["SD Video \n Segment"]
    fs_v_c3["SD Video \n Segment"]
    fs_v_c4["SD Video \n Segment"]
    f_v_c -- "Represents" --> s_v
    f_v_c --- fs_v_c1

    s_m -- "Collects" --> s_v
    s_m -- "Collects" --> s_a

    f_m_a -- "Collects" --> f_a_a
    f_m_b -- "Collects" --> f_a_a
    f_m_c -- "Collects" --> f_a_a
    f_m_d -- "Collects" --> f_a_b
    f_m_e -- "Collects" --> f_a_b
    f_m_f -- "Collects" --> f_a_b
    f_m_a -- "Collects" --> f_v_a
    f_m_b -- "Collects" --> f_v_b
    f_m_c -- "Collects" --> f_v_c
    f_m_d -- "Collects" --> f_v_a
    f_m_e -- "Collects" --> f_v_b
    f_m_f -- "Collects" --> f_v_c

    classDef source fill:#00BF7D,color:#000
    classDef flow fill:#0073E6,color:#FFF
    classDef segment fill:#5928ED,color:#FFF

    class s_m,s_a,s_v source
    class f_m_a,f_m_b,f_m_c,f_m_d,f_m_e,f_m_f,f_a_a,f_a_b,f_v_a,f_v_b,f_v_c flow
    class fs_a_a1,fs_a_a2,fs_a_a3,fs_a_a4,fs_a_b1,fs_a_b2,fs_a_b3,fs_a_b4,fs_v_a1,fs_v_a2,fs_v_a3,fs_v_a4,fs_v_b1,fs_v_b2,fs_v_b3,fs_v_b4,fs_v_c1,fs_v_c2,fs_v_c3,fs_v_c4 segment
```

### Addition of Ancillary or Alternative Audio

`Flows` are logically independent and are associated with other `Flows` via the `collection` mechanism, so new `Flows` can be created to augment your assets at any time.
The synchronisation relationship between two or more `Flows` is encoded into their relationship to a common timeline.
As a result, adding ancillary or alternative audio to a set of media is as simple as creating the new media co-timed with the other items in the set, and introducing a new Multi-Flow (and corresponding Multi-Source) to define the augmented media `collection`.

> [!NOTE]
> In this example, the two Multi-Flows and Sources are representing editorially distinct and useful combinations of media.
This makes the use of multiple Multi-Flows appropriate as opposed to the anti-pattern described above.

```mermaid
block-beta
columns 13
    space:1
    s_m_a["Source \n Multi-essence \n (Original feed)"]
    space:4
    f_m_a["Flow \n Multi-essence \n (Original feed)"]
    space:6
    f_m_a -- "Represents" --> s_m_a

    space:2
    s_m_b["Source \n Multi-essence \n (Feed + AD)"]
    space:2
    f_m_b["Flow \n Multi-essence \n (Feed + AD)"]
    space:7
    f_m_b -- "Represents" --> s_m_b

    space:13

    space:9
    time_dummy_1[" "]
    space:2
    time_dummy_2[" "]
    time_dummy_1 -- "Time" --> time_dummy_2
    style time_dummy_1 fill:none, stroke:transparent;
    style time_dummy_2 fill:none, stroke:transparent;

    s_v["Source \n Video \n (Main)"]
    space:6
    f_v["Flow \n Video \n V210 \n (Main)"]
    space:1
    fs_v_1["Video \n Segment"]
    fs_v_2["Video \n Segment"]
    fs_v_3["Video \n Segment"]
    fs_v_4["Video \n Segment"]
    f_v -- "Represents" --> s_v
    f_v --- fs_v_1

    space:1
    s_a_a["Source \n Audio \n (Production Sound)"]
    space:4
    f_a_a["Flow \n Audio \n AAC \n (Production Sound)"]
    space:2
    fs_a_a1["Audio \n Segment"]
    fs_a_a2["Audio \n Segment"]
    fs_a_a3["Audio \n Segment"]
    fs_a_a4["Audio \n Segment"]
    f_a_a -- "Represents" --> s_a_a
    f_a_a --- fs_a_a1

    space:2
    s_a_b["Source \n Audio \n (Audio Description)"]
    space:2
    f_a_b["Flow \n Audio \n AAC \n (Audio Description)"]
    space:3
    fs_a_b1["Audio \n Segment"]
    fs_a_b2["Audio \n Segment"]
    fs_a_b3["Audio \n Segment"]
    fs_a_b4["Audio \n Segment"]
    f_a_b -- "Represents" --> s_a_b
    f_a_b --- fs_a_b1

    s_m_a -- "Collects" --> s_v
    s_m_b -- "Collects" --> s_v

    s_m_a -- "Collects" --> s_a_a
    s_m_b -- "Collects" --> s_a_a

    s_m_b -- "Collects" --> s_a_b

    f_m_a -- "Collects" --> f_v
    f_m_b -- "Collects" --> f_v

    f_m_a -- "Collects" --> f_a_a
    f_m_b -- "Collects" --> f_a_a

    f_m_b -- "Collects" --> f_a_b

    classDef source fill:#00BF7D,color:#000
    classDef flow fill:#0073E6,color:#FFF
    classDef segment fill:#5928ED,color:#FFF

    class s_m_a,s_m_b,s_a_a,s_a_b,s_v source
    class f_m_a,f_m_b,f_a_a,f_a_b,f_v flow
    class fs_a_a1,fs_a_a2,fs_a_a3,fs_a_a4,fs_a_b1,fs_a_b2,fs_a_b3,fs_a_b4,fs_v_1,fs_v_2,fs_v_3,fs_v_4 segment
```

> [!NOTE]
> It's technically permissible to collect together a mixture of mono- and multi-essence Flows into a higher-level multi-essence Flow.
However, creating multi-level hierarchies like this breeds complexity and will likely impact performance, so it's inadvisable in most cases.
It's generally better to reference the lowest-level mono-essence Flows individually in the multi-essence collection.

### Addition of Video Layers

Video layers or overlays can also be stored as separate `Flows`, synchronised using the same mechanism as in the audio example above.

```mermaid
block-beta
columns 15
    space:1
    s_m_a["Source \n Multi-essence \n (Original feed)"]
    space:6
    f_m_a["Flow \n Multi-essence \n (Original feed)"]
    space:6
    f_m_a -- "Represents" --> s_m_a

    space:2
    s_m_b["Source \n Multi-essence \n (Feed + AD)"]
    space:4
    f_m_b["Flow \n Multi-essence \n (Feed + AD)"]
    space:7
    f_m_b -- "Represents" --> s_m_b

    space:3
    s_m_c["Source \n Multi-essence \n (Feed + Graphics)"]
    space:2
    f_m_c["Flow \n Multi-essence \n (Feed + Graphics)"]
    space:8
    f_m_c -- "Represents" --> s_m_c

    space:15

    space:15

    space:11
    time_dummy_1[" "]
    space:2
    time_dummy_2[" "]
    time_dummy_1 -- "Time" --> time_dummy_2
    style time_dummy_1 fill:none, stroke:transparent;
    style time_dummy_2 fill:none, stroke:transparent;

    s_v_a["Source \n Video \n (Main)"]
    space:8
    f_v_a["Flow \n Video \n V210 \n (Main)"]
    space:1
    fs_v_a1["Video \n Segment"]
    fs_v_a2["Video \n Segment"]
    fs_v_a3["Video \n Segment"]
    fs_v_a4["Video \n Segment"]
    f_v_a -- "Represents" --> s_v_a
    f_v_a --- fs_v_a1

    space:1
    s_a_a["Source \n Audio \n (Production Sound)"]
    space:6
    f_a_a["Flow \n Audio \n AAC \n (Production Sound)"]
    space:2
    fs_a_a1["Audio \n Segment"]
    fs_a_a2["Audio \n Segment"]
    fs_a_a3["Audio \n Segment"]
    fs_a_a4["Audio \n Segment"]
    f_a_a -- "Represents" --> s_a_a
    f_a_a --- fs_a_a1

    space:2
    s_a_b["Source \n Audio \n (Audio Description)"]
    space:4
    f_a_b["Flow \n Audio \n AAC \n (Audio Description)"]
    space:3
    fs_a_b1["Audio \n Segment"]
    fs_a_b2["Audio \n Segment"]
    fs_a_b3["Audio \n Segment"]
    fs_a_b4["Audio \n Segment"]
    f_a_b -- "Represents" --> s_a_b
    f_a_b --- fs_a_b1

    space:3
    s_v_b["Source \n Video \n (Graphics)"]
    space:2
    f_v_b["Flow \n Video \n H264 \n (Graphics)"]
    space:4
    fs_v_b1["Video \n Segment"]
    fs_v_b2["Video \n Segment"]
    fs_v_b3["Video \n Segment"]
    fs_v_b4["Video \n Segment"]
    f_v_b -- "Represents" --> s_v_b
    f_v_b --- fs_v_b1

    s_m_a -- "Collects" --> s_v_a
    s_m_b -- "Collects" --> s_v_a
    s_m_c -- "Collects" --> s_v_a

    s_m_a -- "Collects" --> s_a_a
    s_m_b -- "Collects" --> s_a_a
    s_m_c -- "Collects" --> s_a_a

    s_m_b -- "Collects" --> s_a_b

    s_m_c -- "Collects" --> s_v_b

    f_m_a -- "Collects" --> f_v_a
    f_m_b -- "Collects" --> f_v_a
    f_m_c -- "Collects" --> f_v_a

    f_m_a -- "Collects" --> f_a_a
    f_m_b -- "Collects" --> f_a_a
    f_m_c -- "Collects" --> f_a_a

    f_m_b -- "Collects" --> f_a_b

    f_m_c -- "Collects" --> f_v_b

    classDef source fill:#00BF7D,color:#000
    classDef flow fill:#0073E6,color:#FFF
    classDef segment fill:#5928ED,color:#FFF

    class s_m_a,s_m_b,s_m_c,s_a_a,s_a_b,s_v_a,s_v_b source
    class f_m_a,f_m_b,f_m_c,f_a_a,f_a_b,f_v_a,f_v_b flow
    class fs_a_a1,fs_a_a2,fs_a_a3,fs_a_a4,fs_a_b1,fs_a_b2,fs_a_b3,fs_a_b4,fs_v_a1,fs_v_a2,fs_v_a3,fs_v_a4,fs_v_b1,fs_v_b2,fs_v_b3,fs_v_b4 segment
```

Being able to reference these audio and video layers independently and bind them together in different combinations offers greater flexibility in downstream media workflows, and for future re-use of media assets.

### Clipping Media

A clip of an existing Source may be represented purely in metadata, referencing the existing Media Objects.
A new Source and Flow is created as the clip may be considered editorially distinct.
The new Flow may map the existing Objects to different points on it's timeline.

```mermaid
block-beta
columns 8
    space:4
    dummy1[" "]
    space:2
    dummy2[" "]
    dummy1 -- "Time" --> dummy2
    style dummy1 fill:none, stroke:transparent;
    style dummy2 fill:none, stroke:transparent;

    a_s_a["Source \n Audio \n (BBC Proms R3 Mix)"]
    space:1
    a_f_a["Flow \n Audio \n LPCM Stereo \n (BBC Proms R3 Mix - High Quality)"]
    space:1
    a_fs_a1["Segment \n (LPCM)"]
    a_fs_a2["Segment \n (LPCM)"]
    a_fs_a3["Segment \n (LPCM)"]
    a_fs_a4["Segment \n (LPCM)"]
    a_f_a -- "Represents" --> a_s_a
    a_f_a --- a_fs_a1

    space:8

    space:4
    a_mo_1["Media Object \n (LPCM)"]
    a_mo_2["Media Object \n (LPCM)"]
    a_mo_3["Media Object \n (LPCM)"]
    a_mo_4["Media Object \n (LPCM)"]

    a_fs_a1 -- "References" --> a_mo_1
    a_fs_a2 -- "References" --> a_mo_2
    a_fs_a3 -- "References" --> a_mo_3
    a_fs_a4 -- "References" --> a_mo_4

    space:8

    a_s_b["Source \n Audio \n (BBC Proms Clip)"]
    space:1
    a_f_b["Flow \n Audio \n LPCM Stereo \n (BBC Proms Clip - High Quality)"]
    space:1
    a_fs_b1["Segment \n (LPCM)"]
    a_fs_b2["Segment \n (LPCM)"]
    space:2
    a_f_b -- "Represents" --> a_s_b
    a_f_b --- a_fs_b1

    a_fs_b1 -- "References" --> a_mo_2
    a_fs_b2 -- "References" --> a_mo_3

    classDef source fill:#00BF7D,color:#000
    classDef flow fill:#0073E6,color:#FFF
    classDef segment fill:#5928ED,color:#FFF
    classDef object fill:#00B4C5,color:#000

    class a_s_a,a_s_b source
    class a_f_a,a_f_b flow
    class a_fs_a1,a_fs_a2,a_fs_a3,a_fs_a4,a_fs_b1,a_fs_b2 segment
    class a_mo_1,a_mo_2,a_mo_3,a_mo_4 object
```

### Edit-by-Reference with Multiple Flows

A new cuts-based edit may be created as a new Source and Flow that similarly references existing Media Objects from one or more Flows.
New Objects are only created for media that doesn't currently exist in the store.
Flow Segments could use a subset of the TimeRange available in a referenced Object e.g. only the first 5 seconds of a 10 second Object are needed.

```mermaid
block-beta
columns 9
    space:4
    dummy1[" "]
    space:3
    dummy2[" "]
    dummy1 -- "Time" --> dummy2
    style dummy1 fill:none, stroke:transparent;
    style dummy2 fill:none, stroke:transparent;

    a_s_a["Source \n Audio \n (BBC Proms R3 Ep1)"]
    space:1
    a_f_a["Flow \n Audio \n LPCM Stereo \n (BBC Proms R3 Ep1 - High Quality)"]
    space:1
    a_fs_a1["Segment \n (LPCM)"]
    a_fs_a2["Segment \n (LPCM)"]
    a_fs_a3["Segment \n (LPCM)"]
    a_fs_a4["Segment \n (LPCM)"]
    space:1
    a_f_a -- "Represents" --> a_s_a
    a_f_a --- a_fs_a1

    space:9

    space:4
    a_mo_a1["Media Object \n (LPCM)"]
    a_mo_a2["Media Object \n (LPCM)"]
    a_mo_a3["Media Object \n (LPCM)"]
    a_mo_a4["Media Object \n (LPCM)"]
    space:1

    a_fs_a1 -- "References" --> a_mo_a1
    a_fs_a2 -- "References" --> a_mo_a2
    a_fs_a3 -- "References" --> a_mo_a3
    a_fs_a4 -- "References" --> a_mo_a4

    space:9

    a_s_b["Source \n Audio \n (BBC Proms Highlights)"]
    space:1
    a_f_b["Flow \n Audio \n LPCM Stereo \n (BBC Proms Highlights - High Quality)"]
    space:1
    a_fs_b1["Segment \n (LPCM)"]
    a_fs_b2["Segment \n (LPCM)"]
    a_fs_b3["Segment \n (LPCM)"]
    a_fs_b4["Segment \n (LPCM)"]
    a_fs_b5["Segment \n (LPCM)"]
    a_f_b -- "Represents" --> a_s_b
    a_f_b --- a_fs_b1

    space:9

    space:8
    a_mo_b1["Media Object \n (LPCM)"]

    space:9

    space:4
    a_mo_c1["Media Object \n (LPCM)"]
    a_mo_c2["Media Object \n (LPCM)"]
    a_mo_c3["Media Object \n (LPCM)"]
    a_mo_c4["Media Object \n (LPCM)"]
    space:1

    space:9

    a_s_c["Source \n Audio \n (BBC Proms R3 Ep2)"]
    space:1
    a_f_c["Flow \n Audio \n LPCM Stereo \n (BBC Proms R3 Ep2 - High Quality)"]
    space:1
    a_fs_c1["Segment \n (LPCM)"]
    a_fs_c2["Segment \n (LPCM)"]
    a_fs_c3["Segment \n (LPCM)"]
    a_fs_c4["Segment \n (LPCM)"]
    space:1
    a_f_c -- "Represents" --> a_s_c
    a_f_c --- a_fs_c1

    a_fs_c1 -- "References" --> a_mo_c1
    a_fs_c2 -- "References" --> a_mo_c2
    a_fs_c3 -- "References" --> a_mo_c3
    a_fs_c4 -- "References" --> a_mo_c4

    a_fs_b1 -- "References" --> a_mo_a2
    a_fs_b2 -- "References" --> a_mo_a3
    a_fs_b3 -- "References" --> a_mo_c3
    a_fs_b4 -- "References" --> a_mo_c4
    a_fs_b5 -- "References" --> a_mo_b1

    classDef source fill:#00BF7D,color:#000
    classDef flow fill:#0073E6,color:#FFF
    classDef segment fill:#5928ED,color:#FFF
    classDef object fill:#00B4C5,color:#000

    class a_s_a,a_s_b,a_s_c source
    class a_f_a,a_f_b,a_f_c flow
    class a_fs_a1,a_fs_a2,a_fs_a3,a_fs_a4,a_fs_b1,a_fs_b2,a_fs_b3,a_fs_b4,a_fs_b5,a_fs_c1,a_fs_c2,a_fs_c3,a_fs_c4 segment
    class a_mo_a1,a_mo_a2,a_mo_a3,a_mo_a4,a_mo_b1,a_mo_c1,a_mo_c2,a_mo_c3,a_mo_c4 object
```
