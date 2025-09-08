# Timing in MPEG-TS

> [!NOTE]
> TAMS is highly agnostic to the container format used for media.
> MPEG-TS has, however, emerged as a common choice due to its ease of concatenation and wide support.
> While the information in this application notes refers to MPEG-TS concepts, much of its content will be applicable to other formats.

## MPEG2-TS Packetised Elementary Stream (PES)

In MPEG2-TS, the data 'quantum' is the Packetised Elementary Stream (PES) packet, whose structure is described in [ISO/IEC 13818-1](https://www.iso.org/obp/ui/en/#iso:std:iso-iec:13818:-1:ed-9:v1:en).
The fields of interest in this application note are the `PTS` and `DTS` timestamps.

To support bidirectional inter-frame video coding, PES packets support both a Presentation Timestamp (PTS) and Decode Timestamp (DTS): the `pts_dts_flags` field in the PES header indicates which are present in any given packet.

### Timing Within an MPEG2-TS PES

The ISO/IEC 13818-1 standard indicates that the system frequency shall be in the range
$F_s = 27\times10^6 \pm 810$ Hz.
From this, a system sample timebase of $B_s = \frac{F_s}{300} = 9\times10^5 \pm 2.7$ Hz is derived.
For the rest of this note, we will assume that the times used have no variation (i.e. the sample time base is a perfect 90 KHz).

Both the PTS and DTS timestamps are represented by a 33-bit unsigned integer indicating a number of units of the sample time base, calculated as such:

$$ C_{[P/D]TS} = (T_e \times B_s) \mod 2^{33} $$

where $T_e$ is the time in seconds since the epoch.

An alternate way to envision this is to think of the timestamp fields storing only the lowest 33-bits of an absolute timestamp in MPEG-TS samples, e.g.:

$$ C_{[P/D]TS}  = (T_e \times B_s) \cdot \text{0x1 FFFF FFFF} $$

Where $\cdot$ is the bitwise AND operation.

The obvious consequence of this is that the timestamp on its own can _not_ be used to uniquely identify any given media unit: the timestamps will roll-over every ~26.5 hours.

## The `ts_offset` Field

In TAMS, we must be able to reconstruct the absolute timestamp of any given PES packet.
To facilitate this, each Flow Segment in a TAM store which carries MPEG2-TS media contains a `ts_offset` field.
As stated in the above section, we can imagine that the PTS/DTS fields are simply the lower 33 bits of some absolute timestamp, so if we can carry the upper bits we can use those to generate the absolute timestamp.

This is initially done when generating the flow segments, where the absolute timestamp is known.
For the earliest **presentation** timestamp in a segment, an 'absolute' PTS is generated, which can then be used to calculate a 'base' sample count for that segment:

$$ C_{offset} = C_{PTS_{0}} - (C_{PTS_{0}} \cdot \text{0x1 FFFF FFFF}) $$

Where $C_{PTS_{0}}$ is the PTS sample count of the first PES packet in the Flow Segment, and $\cdot$ is the bitwise AND operator.

The $C_{offset}$ is then converted into a TAMS Timestamp utilising the `.from_count` [method provided in the public `mediatimestamp` repository](https://bbc.github.io/rd-apmm-python-lib-mediatimestamp/mediatimestamp/mediatimestamp.html#Timestamp.from_count): effectively this represents $T_{offset}$, the time since the epoch:

$$ T_{offset} = \frac{C_{offset}}{B_s} $$

which is then processed into a `sec:nanosec` timestamp.
This can be thought of as the last time the 33-bit counter 'rolled over'.

Working backwards, the absolute timestamp for any given PTS or DTS $n$ can be reconstructed as such:

$$T_{PTS_{n}} = T_{offset} + \frac{C_{PTS_n}}{B_s} $$

### Rollover

It is possible that the counter will roll over mid-segment.
As such, simply using the equations outlined above will result in incorrect timestamps.
To account for this, a decoder could, for example:

```text
TS_OFFSET = FLOW_SEG.ts_offset

FOR EACH PTS
    IF (PTS < LAST_PTS) AND (LAST_PTS > 2^33-2^31) THEN
        TS_OFFSET = TS_OFFSET + ((2^33-1)/90000) SECONDS
    END IF
    TIMESTAMP = GET_TIMESTAMP(PTS, TS_OFFSET)
    LAST_PTS = PTS
END FOR

```
