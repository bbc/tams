# When TAMS is a good fit for non-media data. And when it’s not

## Abstract

TAMS places few restrictions on the type of content stored within it.
It has been developed primarily with audio and video in mind.
But there are other types of timeline-based content one might wish to store in their media workflows.
When is it appropriate to store these other types of content in TAMS?

## Considerations

### Indexing of content

TAMS indexes Flows as a whole using a small number of pieces of metadata (Flow/Source ID, tags, etc.), however the only index that can be used inside a specific Flow is time.
It is not possible to query the data/content or metadata as it applies to a portion of the Source/Flow, which would be needed to query timeline-based metadata (e.g. it's not possible to query a transcript for occurrences of a specific word using TAMS).
As such, TAMS is usually not appropriate for the storing of timeline-based metadata.
However some examples of where it may be appropriate are given below.

### Segment size

TAMS may be a good fit for querying some types of content.
But it might not be an efficient storage mechanism.
Typically, the content being stored should be larger than the metadata stored alongside it.

## Examples

### Timed Text

Timed text, such as closed captions, is relatively low data rate.
But it is often used alongside audio and video, using similar workflows.
Existing live workflows in television broadcast facilities may make use of [SMPTE 2110-43](https://ieeexplore.ieee.org/document/9521125)/[RFC8759](https://www.rfc-editor.org/rfc/rfc8759.html) to carry small independently decodable XML documents containing the captions.
The usage patterns, recommended frequency, and likely size of these documents lend themselves well to storage in a TAMS store, however care should be taken to balance the flexibility of shorter Segments (and smaller XML documents) against the increased metadata storage overhead.

### Time-based metadata

Consider a workflow that records who appears on screen at particular times.
This type of data likely wouldn't be appropriate to store in TAMS, as you would not be able to efficiently perform basic queries such as what times an individual appeared on screen.

Time Addressable Metadata is an important complimentary concept to Time Addressable Media.
But it is not within the scope of this repository or specification.

### Logging/metering

Consider a system which records loudness levels of audio a small number of times a second.
If a Segment length of ~1 second was used, common for media stored in TAMS to enable efficient random access, then the Segment metadata may be many times larger than the Segment content.
The underlying file object store may end up storing a large number of very small objects.
This is often inefficient both in resources, and cost.
Using larger Segments would bring about different issues.
Segments normally only become available once they are complete.
A large Segment size will, therefore, increase the latency in Segments becoming available.
TAMS would not be appropriate for such low rate data.

### High data rate production data

Consider an alpha mask, such as those produced by a chroma-key process.
Carrying the alpha channel in it's related video Flow would increase it's data rate significantly.
But the alpha channel likely wouldn't be used by many parts of your production workflow.
Carrying the alpha channel in a separate Flow would make it available to parts of the production workflow that need it, without wasting bandwidth for those which don't.
Usage patterns, and data rates for this video-like Flow would lend itself well to storage in TAMS.
