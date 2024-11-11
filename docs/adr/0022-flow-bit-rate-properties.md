---
status: "proposed"
---
# Flow Bit Rate Properties

## Context and Problem Statement

The current specification of a Flow includes the `avg_bit_rate` and `max_bit_rate` properties.
The specification does not define in detail what these values represent.
The purpose of this ADR is to provide some clarity to what these properties are, providing improved interoperability by avoiding differing and incompatible interpretations.

A question that needs answering is whether the bit rates are for the essence data, the segments or both.

The TAMS generally stores media in segments.
A question is whether the properties in HLS and DASH are applicable to TAMS where the segments may not have the same restrictions to support delivery to end-user clients.
In the most extreme case, a Flow could be stored as a single segment like a regular media file.

### Essence Bit Rates

One interpretation of these properties is that they measure media essence (e.g. H.264 and AAC) bit rates.
These properties relate to the essence only but don't account for the container overhead or network conditions.

Essence bit rate information can be carried in the coded bitstream, such as the `hrd_parameters` structure in the H.264 bitstream that specifies the maximum bit rate into the CPB (Coded Picture Buffer) in the HRD (Hypothetical Reference Decoder).

Essence bit rate information can also be found in the container.
The MXF AVC (H.264) sub-descriptor defined in SMPTE ST 381-3 includes the `AVC Maximum Bitrate` and `AVC Average Bitrate` properties.
MP4 / Quicktime has a `btrt` box that includes `Max bit rate` and `Average bit rate` properties.
The MPEG-4 Systems (ISO/IEC 14496-1) defines a descriptor containing `maxBitRate`, `avgBitRate` and `bufferSizeDB` properties; this descriptor can be included in the MP4 / Quicktime `esds` box.

### Segment Bit Rates

Another interpretation of these properties is that they measure media segment (e.g. MPEG-TS and fMP4) bit rates.
These properties relate to the segment files that contain the media essence but don't account for network conditions.

The HLS (HTTP Live Streaming) specification includes a required `BANDWIDTH` Variant Stream property that specifies the largest sum of `peak segment bit rate` values.
The `AVERAGE-BANDWIDTH` Variant Stream property specifies the largest sum of `average segment bit rate` values.
HLS also defines a required `EXT-X-TARGETDURATION` tag that specifies the target maximum segment duration.

The DASH (Dynamic Adaptive Streaming over HTTP) specification includes a `bandwidth` Representation attribute and `minBufferTime` MPD attribute that together specify the sufficient conditions that allow continuous playback after buffering `minBufferTime` with a constant bit rate channel with bit rate equal to `bandwidth`.
DASH also specifies a `maxSegmentDuration` MPD attribute that specifies the maximum segment duration in any media Representation.

The SCTE 214-1 (Society of Cable Telecommunications Engineers) "MPEG DASH for IP-Based Cable Services, Part 1: MPD Constraints and Extensions", section 10.3, is a useful resource to understand the DASH and HLS properties and how they can be used to calculate receiver buffer size or buffer times for continuous playback (under ideal network conditions).
The SCTE 214-1 specification adds a DASH extension `maxSegmentRate` (note that `Rate` is bit rate) Representation attribute to DASH that comparable to the HLS `BANDWIDTH` property (but applies to a single Representation).

## Considered Options

* Option 1: Leave the definition of bit rates to be provided externally.
* Option 2: Define essence bit rates.
* Option 3a: Define segment bit rates.
* Option 3b: Define segment bit rates with target segment duration.
* Option 3c: Define segment bit rates with segment size.
* Option 3d: Define segment bit rates with max segment duration.
* Option 4: Define both essence and segment bit rate properties.

## Decision Outcome

Currently favouring "Option 3b", because it allows a receiver to estimate the buffer size using the maximum bit rate and target segment duration.
Option 3c may be chosen if segment size is a requirement.

### Implementation

tbd

## Pros and Cons of the Options

### Option 1: Leave the definition of bit rates to be provided externally

This is the current state
The definition is left to the applications using TAMS.

* Good, provides flexibility for applications to decide what bit rate definition is most relevant and useful
* Bad, reduces interoperability because the property definition in use may be unknown, which leads to values being misinterpreted or ignored
* Bad, multiple definitions need to be supported for different applications, increasing the implementation burden

### Option 2: Define essence bit rates

The `avg_bit_rate` is calculated as `int(total_essence_bit_size / (total_essence_duration_sec * 1000))` (kbit/sec) of essence data in the Flow.

The `avg_bit_rate` could be calculated from the essence data that is present in the TAMS.
The value could be an expectation of what could be present in the TAMS (e.g. derived from an encoder setting for a live ingest).
The value could be an approximation.
The value could change over time as essence data becomes available or is removed from TAMS.

The `max_bit_rate` is calculated as `max(max_bit_rate, int(window_essence_bit_size / 1000))` for any 1 second time window of essence data.

This definition is similar to the MPEG-4 Systems (ISO/IEC 14496-1) `maxBitRate`, which supports different essence types when compared with something like `AVC Maximum Bitrate` in MXF that is specific to H.264 and the HRD.

The `max_bit_rate` can be interpreted as the bit rate for a constant bit rate network channel that along with a 1 second buffer is sufficient to support continuous playback.

The `max_bit_rate` could be calculated from the essence data that is present in the TAMS.
The value could be an expectation of what could be present in the TAMS (e.g. derived from an encoder setting for a live ingest).
The value could be an approximation, ideally an upper bound (e.g. the bit rate from the H.264 `hrd_parameters`).
The value could change over time as essence data becomes available or is removed from TAMS.

* Good, provides bit rate information that is independent of the container, allowing it to be used in streaming contexts where no or a different media container is used
* Bad, it doesn't directly provide bit rate information for users of TAMS where the segments are the means for accessing essence

### Option 3a: Define segment bit rates

The `avg_bit_rate` is calculated as `int(total_segment_bit_size / (total_segment_duration_sec * 1000))` (kbit/sec) for the segments of the Flow.

The `avg_bit_rate` could be calculated from the segments that are present in the TAMS.
The value could be an expectation of what could be present in the TAMS (e.g. derived from an encoder / muxer setting for a live ingest).
The value could be an approximation.
The value could change over time as segments becomes available or are removed from TAMS.

The `max_bit_rate` is calculated as `int(peak_segment_bit_rate / 1000)`.
The `peak_segment_bit_rate` corresponds to the definition in HLS, where it is defined as the maximum bit rate for a contiguous sequence of segments that has a duration between 0.5 and 1.5 the target segment duration.
The HLS definition is extended to include single segments above 1.5 the target segment duration to handle Flows that don't follow the HLS retrictions for segment durations, e.g. segmentation optimised for best quality, with variable and potentially large GOP sizes etc..

The `max_bit_rate` could be calculated from the segments that are present in the TAMS.
The value could be an expectation of what could be present in the TAMS (e.g. derived from an encoder / muxer setting for a live ingest).
The value could be an approximation, ideally an upper bound (e.g. the bit rate from the H.264 `hrd_parameters` plus some container overhead approximation).
The value could change over time as segments become available or are removed from TAMS.

* Good, provides bit rate information for TAMS users that access essence via segments
* Bad, the information provided by the Flow is incomplete and doesn't allow the bit rate to be used to decide how much segment data needs to be buffered in the receiver for example
* Bad, it doesn't directly provide essence bit rate information for users of TAMS where the essence in other contexts is not transmitted in the same segments as TAMS

### Option 3b: Define segment bit rates with target segment duration

In [Option 3a](#option-3a-define-segment-bit-rates) the `max_bit_rate` on it's own doesn't provide sufficient information to calculate the size or duration of the receiver buffer needed to allow for continuous playback (under ideal network conditions).
The descriptions and calculations from SCTE 214-1 section 10.3 provides insights to what information could be provided.

A [_tams_segmentation_rate](../appnotes/0003-tag-names#_tams_segmentation_rate) Flow tag is currently used in some applications to provide a target segment rate for the Flow.
This segment rate provides the target segment duration (1 / segment rate) that is used to calculate the `max_bit_rate`.
The proposal is to add a `segment_duration` (rational, seconds) property that specifies the target segment duration for the Flow.
A duration is used rather than a rate to avoid confusion with bit and frame rates and to match the descriptions and properties in the HLS and DASH specifications.
A rational type allows more precise values to be set (e.g. to match frames rates), avoiding potential rounding issues when doing calculations over long periods of time.

The description in SCTE 214-1 section 10.3 includes a formula for calculating the buffer size required for continuous playback.
The buffer size is defined as `1.1 * MSR[R] * SDmax`.
`MSR[R]` in the TAMS context is `max_bit_rate`, `SDmax` is the maximum segment duration and `1.1` adds a 10% overhead for additional event data.
The proposal is to add a `max_segment_duration` (floating point, seconds) property that provides the maximum segment duration (`SDmax`) for the Flow.
The variation in segment duration is assumed to be between 0.5 and 1.5 the segment_duration.
The `SDmax` is approximately `segment_duration * 1.5` and the minimum buffer size in bytes is then approximately `max_bit_rate * 1000 * SDmax * 8`.

Would a property equivalent to `minBufferTime` in DASH be useful as well?

In summary, this option extends [Option 3a](#option-3a-define-segment-bit-rates) with this property:

* `segment_duration` (rational, seconds): the target segment duration for segmenting the Flow media

* Good, provides information about the segments that allows the bit rate information to be used to estimate receiver buffer sizes required for continuous playback (not taking network conditions into account)
* Bad, it doesn't directly provide essence bit rate information for users of TAMS where the essence is transmitted by other means

### Option 3c: Define segment bit rates with segment size

SCTE 214-1 puts limits on the segment size so that they don't exceed the buffer size.
The TAMS doesn't require media to be segmented in a way that is compatible with the restrictions applied to HLS and DASH segments.
Some applications my optimise segments for throughput rather than taking latency into account.
E.g. a 10 MB segment size may be the optimal segment size for an object store for maximum throughput.
The proposal is to add `segment_size` (integer, bytes) and `max_segment_size` (integer, bytes) properties for applications that segment based on size rather than duration.

In summary, this option extends [Option 3b](#option-3b-define-segment-bit-rates-with-target-segment-duration) with these properties:

* `segment_size` (integer, bytes): the target segment size for segmenting the Flow media
* `max_segment_size` (integer, bytes): the maximim segment size in TAMS for the Flow

* Good, provides information about the segments optimised for size rather than duration
* Good, provides information about the minimum buffer size required to accommodate a single segment
* Neutral, the properties may not be used

### Option 3d: Define segment bit rates with max segment duration

In this option the maximum segment duration is provided explicitly by the `max_segment_duration` property rather than assuming the maximum size variation being `segment_duration * 1.5`.
The `SDmax` is then approximately `min(segment_duration * 1.5, max_segment_duration)`

In summary, this option extends [Option 3b](#option-3b-define-segment-bit-rates-with-target-segment-duration) with this property:

* `max_segment_duration` (floating point, seconds): the maximum segment duration in TAMS for the Flow

* Good, provides information about the segments that allows a more accurate bit rate estimate
* Good, the calculations would not break down once segments exceed the 1.5 times the `segment_duration`.
* Neutral, the property may not be used

### Option 4: Define both essence and segment bit rate properties

TAMS should support a wide range of applications as possible.
This option combines [Option 2](#option-2-define-essence-bit-rates) with [Option 3b](#option-3b-define-segment-bit-rates-with-target-segment-duration) to allow bit rate information to be provided for both essence data and segments.

The `avg_bit_rate` property is split into `avg_essence_bit_rate` and `avg_segment_bit_rate` properties.
The `max_bit_rate` property is split into `max_essence_bit_rate` and `max_segment_bit_rate` properties.

Should there be a recommendation to always set `max_segment_bit_rate`?
This corresponds to the required `BANDWIDTH` variant stream property in HLS and required `bandwidth` Representation property in DASH.
