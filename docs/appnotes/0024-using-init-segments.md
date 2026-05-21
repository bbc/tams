# 0024: Using Media with Initialisation Segments in TAMS

> [!NOTE]
> There is an unfortunate overlap in terminology between TAMS and CMAF/DASH/HLS/fMP4.
> As such, where Segments or Flow Segments are referred to capitalised this document is referring to the TAMS resource types.
> Where init segments or media segments are referred to in lower case, this document is referring to the CMAF resource types.
> Where this document refers to Media Objects or Objects, it is referring to the TAMS Media Object resource type.
> Objects (without Media prepended) has been preferred when referring Objects containing initialisation segments to avoid potential confusion "init Media Object" may cause.
> There is no implied distinction between Media Object or Objects in the TAMS API.
<!-- markdownlint-disable-line -->
>[!NOTE]
> This Application Note refers to CMAF, MPEG-DASH, HLS, and fMP4.
> It also uses terms of art from those formats.
> It should, however, be read as applying to the general case of any format that uses equivalent concepts of initialisation segments.
<!-- markdownlint-disable-line -->
> [!IMPORTANT]
> This Application Note assumes basic knowledge of how to write/read media to/from a TAMS service.

Some media formats, such as [CMAF](https://www.iso.org/standard/85623.html) compatible MPEG-DASH and fMP4, split content into initialisation (init) segments and media segments.
The init segments contain parameters used to configure decoders common across the stream of media
The media segments generally contain the media itself with additional configuration parameters specific to that media segment.
The split of configuration parameters between init and media segments varies according to the profile used.
When the configuration changes, a new init segment may be required.
While a change in technical parameters would generally require a new Flow in TAMS, some init segment changes may be minor codec parameter changes which would not warrant a new Flow.
A change in init-segment will normally result in a new "period" in DASH, or a "discontinuity" in HLS.
Other formats may have similar concepts.

Additionally, technologies implemented as extensions to init segments may result in a new init segment for non-technical changes.
One example being C2PA signing of live media (specifically fragmented MP4, applicable in segmented TAMS use cases).
C2PA uses cryptography to verify the provenance of media.
One of the two C2PA live profiles places cryptographic keys in the init segment which may be used to verify media segments and their sequencing.
When that cryptographic key is rotated, a new init segment will be published.
See [C2PA Section 19](https://spec.c2pa.org/specifications/specifications/2.4/specs/C2PA_Specification.html#live-video) for more information on using C2PA with live media.

TAMS support for init segments makes use of our existing Media Object resource to store and re-use init segments.
These are then associated via their ID to media segment Objects.
This allows existing Media Object re-use mechanisms (i.e. edit-by-reference) to continue to function.
Init segments follow the media.
A client may then detect if the init segment has changed by observing if the init Object ID remains the same or changes between subsequent Flow Segments.

## General Workflows

The general workflows described here refer to init and media segments in isolation from manifests used by specific media formats.
The approaches have, however, been designed to map to manifests where required.

### Write

1. [Register the Flow](https://bbc.github.io/tams/main/index.html#/operations/PUT_flows-flowId)
    * The `init_segments` essence parameter MUST be set to `true`
    * The `container` parameter MUST be set to the mime type of the media segments
2. [Request storage for the init segment(s)](https://bbc.github.io/tams/main/index.html#/operations/POST_flows-flowId-storage)
    * The `content-type` MUST be set to the mime type of the init segment(s)
    * If the mime type of the init segment(s) matches that of the media segments, this step may be skipped and storage for media and init segments requested together
3. Upload the init segment(s)
4. [Request storage for the media segments](https://bbc.github.io/tams/main/index.html#/operations/POST_flows-flowId-storage)
    * `content-type` MUST NOT be set
5. Upload the media segments
6. [Register the media segments as Flow Segments](https://bbc.github.io/tams/main/index.html#/operations/POST_flows-flowId-segments)
    * `object_id` must be set to the Object ID of the media segment
    * `init_object_id` must be set to the Object ID of the init segment
    * Init segment objects should be reused wherever possible

### Read

1. [Get the Flow Segments listing for the Flow](https://bbc.github.io/tams/main/index.html#/operations/GET_flows-flowId-segments)
2. For each Flow Segment
    1. If init segment Object ID has changed
        1. Get init segment Object
        2. (Re)initialise decoder with init segment
    2. Get media segment Object
    3. Perform [media timeline mapping](https://github.com/bbc/tams/#flow-and-media-timelines) as usual in TAMS
    4. Play media segment
