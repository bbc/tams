# Media Objects should be independently decodable. Here's why

## Abstract

TAMS is largely agnostic to the content stored in it.
It is possible to store Segments that aren't independently decodable.
But there are significant benefits if Segments ARE independently decodable.
This app-note explores some of those benefits, as well as some drawbacks.

## Benefits

### Simple operations don't need media knowledge

Consider a basic store transfer operation for a partial Flow.
The simplest approach to this is to copy over the Flow metadata, and download and upload the relevant Segments.
In its most simple form, this operation can be performed in a generic way for any content without media-specific knowledge as long as the content is independently decodable.

If Segments are not independently decodable they, by definition, depend on Segments either side to be decoded.
In this case, the copy software would require the ability to decode the Segment to identify if all Segments needed to decode the required part of the Flow.
This adds inefficiency as the transfer can no longer be purely a store-to-store operation.
It must go via an additional system which (at least partially) decodes the media.

Additionally, TAMS supports copy-by-reference for simple clipping and edit operations.
Where a new Flow references existing Segments in the store.
This is a metadata only operation.
Use of Segments that are not-independently decodable may hamper the use of this feature.

### Ease of playback

With independently decodable Media Objects, it is possible to download a given Segment and play it back.
This makes playback extremely simple, with Segments being fed into the decoder with little/no processing.
Additionally, you do not have to search back/forward to find key-frames needed for playback.

### Resiliency

Having independently decodable Segments reduces the impact of corrupted/missing Segments.
Where Segments are not independently decodable, a corrupted/missing Segment may result in adjacent Segments being unplayable.
This would result in a larger unplayable section of media than if all Segments are independently decodable.

### Compatibility with HLS

HLS is commonly used for streaming media.
It is possible to construct a HLS file from TAMS data, referring to TAMS Objects.
The HLS spec states "The server SHOULD attempt to divide the source media at points that support effective decode of individual Media Segments, such as on packet and key frame boundaries".
Some common HLS profiles only support Segments are independently decodable.

## Drawbacks

### Codec support

Some codecs, and some configurations of codecs, do not support small independently decodable GOPS.
And AAC frames require data from previous and next frames to decode without introducing artefacts.
This is why independently decodable Segments are recommended, but not mandated by TAMS.

### Potentially higher write latency

Where long GOPs (Group of Pictures) or infrequent decoder refreshes, independently decodable Segments may incur higher latency.
This is because you must wait for the entire independently decodable portion of the media to be available before you close out the Segment.
That is to say your GOP-length places a minimum size on your Segments, and latency on your ingest.
