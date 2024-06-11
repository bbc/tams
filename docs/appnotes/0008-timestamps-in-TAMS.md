# 0008: Timestamps in TAMS

## Abstract

The Time-Addressable Media Store uses time as a primary index for media of any type, whether it originated as a live stream or a static file.
As well as providing consistency for referencing live and pre-stored media, using time directly decouples us from the details of frame rates and sample rates at the point of access, making the API agnostic of media type or format.
Applying timestamps sampled from a common clock across several Flows also embeds synchronisation relationships without having to physically bind the media together.
This scheme allows for a great deal of flexibility in managing and processing media in different combinations.
But what do we mean by time in this context?
What are the constraints and expectations of how we timestamp media in TAMS to deliver these benefits?

This app note relates only to the capabilities of the existing specification, and the assumptions they are based upon.
Future work may extend the specification to allow more explicit signalling of timing mechanisms and modes, but consideration of these is out of scope of this document.

## Content

### Timestamps

A timerange is associated with each media segment written, in the body of the POST request to register the segment.
See the API documentation for [FlowSegments](https://bbc.github.io/tams/4.0/index.html#/operations/POST_flows-flowId-segments) for more details.

### Resolution

The time-resolution of the clock or counter used to generate timestamps and timeranges must be at least double that of the highest media (or data) unit rate, to avoid problems with aliasing.
Since TAMS is designed to support any media unit rate, time values are recorded at nanosecond resolution.
Timeranges are represented using a pair of timestamps separated by an underscore, with markers for inclusivity and exclusivity.
A high-resolution timestamp is easily converted to/from a media unit count for display or other purposes.
See [the open-source mediatimestamp library](https://github.com/bbc/rd-apmm-python-lib-mediatimestamp) for more details of formats and conversion routines.

### Uniqueness & linearity

Since time is used as an index in TAMS, it's important that the clock or counter used is linear (strictly increasing without gaps or jumps), and that the mapping between timestamps and media objects is unique i.e. there can be no overlaps in the timeranges covered by media objects on the Flow timeline.
To support long-running Flows, the timestamp format used by TAMS is based on that used in [Precision Time Protocol](https://en.wikipedia.org/wiki/Precision_Time_Protocol), using 48 bits to represent seconds with 32 bits for nanoseconds.
This provides an extremely large range of possible values of seconds.
The default PTP epoch, determining the alignment of the origin of the PTP timescale with time of day, is 1 January 1970 00:00:00.
This epoch is also used by SMPTE in standards covering the use of PTP for media applications.

PTP is based on the [TAI](https://en.wikipedia.org/wiki/International_Atomic_Time) timescale to avoid being subject to [leap seconds](https://en.wikipedia.org/wiki/Leap_second), thereby preserving linearity even in cases where Flow timelines cross a leap second boundary.
The result of this is that UTC timestamps and PTP timestamps relating to the same time of day differ by the number of leap seconds that have occurred since the epoch.
As of today this offset amounts to 37 seconds, but that will change when the next leap second is introduced by the relevant authority.

It's important to note that while TAMS was designed to support the use of TAI, there is no reason why other timescales can't be used as long as they are linear across the entire timerange used in a given project.
At present there is no mechanism in the core schemas to indicate the timescale used, so it would be unwise to use a mixture of TAI and UTC in a single project.

### Inter-Flow synchronisation

One of the key benefits of using time as an index is that we can describe synchronisation relationships between independent elements, and those elements can be freely processed, combined or added to in a multitude of different ways, without having to repeatedly re-sync and re-mux.
To achieve this, all we need to do is to map each Flow of media to a common timeline.
To put it another way, we need to use a common clock to derive the timestamps for all Flows in a given set.

The timestamps may be sampled from the clock or they may be synthesised (for example in the case of file ingest) using a counter starting from a pre-agreed value incrementing in steps that correspond to the media unit rate.
Where synchronisation relationships between media need to be created rather than captured (for example when adding additional elements like graphics layers or audio description), the timestamps may be generated or modified on ingest to align with the pre-existing timeline.

> ![NOTE:](../images/NOTE.svg) Since time is used as the primary index and Flows are immutable, it follows that timeshifting the media necessitates the creation of a new Flow.
Flows are co-timed representations of Sources, so this operation will also require a new parent Source to be created.
See the appnote [Practical Application of the TAMS Content Model](./0001-multi-mono-essence-flows-sources.md) for further information about Flows and Sources.
There is no need to copy the underlying media objects to achieve a simple timeshift.
The original media objects can be referenced from the new Flow timeline.

### Real-time clock vs synthetic timelines

While in some circumstances timestamping with the current time of day (from the chosen epoch) is convenient, natural and useful, it is by no means mandatory that the timestamps are meaningful in relation to time of day.
When we're dealing with live streams, in some cases using time of day provides additional benefits, for example when we want to make the link between the media we're handling and other events that are happening simultaneously.
When working with content that originates from a file, linking the timeline to time of day may make less sense, unless we're dealing with a mixture of files and streams.

### Clock quality

There are several challenges raised by timestamping media streams from a real time clock.
The quality of the clock is important: its accuracy and its traceability to a global time reference such as GPS affect the reliability of the derived time values.
Traceability is particularly important if we will be reliant on comparisons between timestamps sourced from different clocks, for example where media Flows are timestamped in different locations.
Accuracy of clock frequency, clock stability and level of jitter needs to be good enough to support timestamp calculations and comparisons at the desired level of resolution.

### Timestamp sampling

Perhaps the most important consideration for live media is the point at which timestamps are associated in relation to its inception.
Ideally timestamps would be derived from a traceable real time clock at the point the media comes into existence, and bound to the media from that point forward, over streaming links and into storage.
This directly associates the act of acquiring the pictures or the sound with the time it happened in the real world.
However, this is not always possible or practical (and also doesn't cover all media production scenarios), so we often need to inject timestamps further downstream.
But this creates a problem: we generally have no way of knowing how much delay the media may have been subjected to before the point at which the timestamps are injected.
As a result, synchronisation relationships may be mis-registered.

The key principle to adhere to wherever possible is to apply timestamps at a point where the desired synchronisation relationship between elements is known, for example when elements are ingested from a multiplexed, internally-synchronised feed.

A longstanding ad-hoc approach to solving the problem of synchronisation across a set of feeds has been a combination of video genlock and embedding of SMPTE ST 12-1 timelabels from a timecode signal distributed to every media acquisition device.
While this technology has limitations, embedded timecode can be used in conjunction with a high-resolution clock at the point of ingest to ensure that the desired inter-feed synchronisation relationship is captured.

BBC R&D have recently been experimenting with the use of TEMI (Timed External Media Information) that specifies a standard way to embed high-resolution timeline information into MPEG2-TS streams.
This has the potential to provide a more flexible and comprehensive solution to the in-stream carriage of timing information to inform the timeline stored in TAMS.
TEMI is specified in [ISO/IEC 13818-1 (ITU-T-REC-H222.0)](https://www.itu.int/rec/T-REC-H.222.0-201808-S) Annex U.

### Timestamp regularisation

For Flows with a constant media unit rate, timestamp calculations and comparisons may be streamlined by regularising Flow timestamps to align to media unit boundaries from the chosen epoch.
This has the effect of eliminating phase offsets and timing jitter.
Once timestamps have been regularised in this way subsequent conversions between high-resolution time and media units are reversible.
Of course, if tracking phase difference and/or jitter are important for your use case the timestamps should be stored unadulterated and they can be regularised locally where necessary.
