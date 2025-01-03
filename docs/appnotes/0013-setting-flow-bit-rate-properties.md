# Setting Flow Bit Rate Properties

It was decided in the [Flow Bit Rate Properties](../adr/0022-flow-bit-rate-properties.md#) ADR to follow [option 3b](../adr/0022-flow-bit-rate-properties.md#option-3b-define-segment-bit-rates-with-target-segment-duration).
Option 3b defines the `max_bit_rate` and `avg_bit_rate` Flow properties to be segment bit rates (rather than essence bit rates).
Option 3b adds a `segment_duration` Flow property that is the target duration for the segments.
The `segment_duration` and `max_bit_rate` can be used for calculating a minimum receiver buffer size.

This AppNote defines how clients can calculate the bit rates if they are not known from the process that is creating them (e.g. an encoder).

Further background on the definition and calculations can be found in the [Flow Bit Rate Properties](../adr/0022-flow-bit-rate-properties.md#) ADR.

## Setting Average Bit Rate

The `avg_bit_rate` is calculated as `int(total_segment_bit_size / (total_segment_duration_sec * 1000))` (kbit/sec) for the segments of the Flow.

The `avg_bit_rate` could be calculated from the segments that are present in the TAMS.
The value could be an expectation of what could be present in the TAMS (e.g. derived from an encoder / muxer setting for a live ingest).
The value could be an approximation.
The value could change over time as segments becomes available or are removed from TAMS.

## Setting Maximum Bit Rate

The `max_bit_rate` is calculated as `int(peak_segment_bit_rate / 1000)`.
The `peak_segment_bit_rate` corresponds to the definition in HLS ([HTTP Live Streaming](https://datatracker.ietf.org/doc/html/rfc8216)), where it is defined as the maximum bit rate for a contiguous sequence of segments that has a duration between 0.5 and 1.5 the target segment duration.
The HLS definition is extended to include single segments above 1.5 the target segment duration to handle Flows that don't follow the HLS retrictions for segment durations, e.g. segmentation optimised for best quality, with variable and potentially large GOP sizes etc..

The `max_bit_rate` could be calculated from the segments that are present in the TAMS.
The value could be an expectation of what could be present in the TAMS (e.g. derived from an encoder / muxer setting for a live ingest).
The value could be an approximation, ideally an upper bound (e.g. the bit rate from the H.264 `hrd_parameters` plus some container overhead approximation).
The value could change over time as segments become available or are removed from TAMS.

## Setting Segment Duration

The `segment_duration` is the media segment duration that the media segmenter (e.g. encoder) is targetting.

The segment durations may vary, e.g. to ensure that video segments with variables size GOPs always start with a key frame.

## Calculating Buffer Size for Continuous Playback

The description in SCTE 214-1 ([Society of Cable Telecommunications Engineers, MPEG DASH for IP-Based Cable Services, Part 1: MPD Constraints and Extensions](https://account.scte.org/standards/library/catalog/scte-214-1-mpeg-dash-for-ip-based-cable-services-part1-mpd-constraints-and-extensions/)), section 10.3 includes a formula for calculating the buffer size required for continuous playback.
The buffer size is defined as `1.1 * MSR[R] * SDmax`.
`MSR[R]` in the TAMS context is `max_bit_rate`, `SDmax` is the maximum segment duration and `1.1` adds a 10% overhead for additional event data.
The duration of segments is assumed to vary between 0.5 and 1.5 times the `segment_duration`.
The `SDmax` is therefore approximately `segment_duration * 1.5` and the minimum buffer size in bytes is then approximately `max_bit_rate * 1000 * SDmax * 8`.
