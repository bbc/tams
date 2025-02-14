# Tags, how to use them, and how we manage them

## Abstract

Tags are intended to be used to add additional metadata to Flows or Sources beyond that which is present in the core API.
This may be to add implementation specific metadata, or to trial metadata fields before they are elevated to the core API.
This application note describes how tags should be used, our process for managing them, and lists currently known tags.

## Usage in implementations

Tags should be considered an extension of the core TAMS metadata.
As such, implementations might not implement specific tags.
Reliance on specific tags should be agreed when integrating implementations.
Implementers should make use of existing tags where possible.

## Maintenance of this list

Where functionality of an existing tag needs to be extended/modified, follow the ADR process to propose an update to this list.

New tags should be added via a Pull Request.
Where tags are intended to implementation specific, prepend the tag with an underscore and the service name (e.g. `_<service_name>_tag_name`).
Where tags are intended to be interoperable, you should usually include an ADR in your PR explaining the decision to add the tag, and the decisions made regarding it's use.

Where a tag gains widespread use, we should consider elevating it to the core API metadata via an ADR.
This will allow for the tag's use to be "locked down", and for changes to be managed as part of the release process.

## Tag statuses

The tags below are marked with the following statuses:

* **In use**:
  * In common usage
  * ADR where this tag was proposed is stated where available
* **Proposed**:
  * Not yet in common usage, but use should be considered
  * ADR where this tag was proposed is stated where available
* **Experimental**:
  * Created for an experimental implementation or application
  * Tag may never be proposed
  * Tag may be proposed in future, possibly with a different name or meaning
  * Tag may appear in one or more implementations or versions
* **Deprecated**:
  * Tag is deprecated and should no longer be used
  * Tag *may* still appear e.g. in old Flow/Source entries
  * Usually the result of a tag being elevated to the core API's metadata
* **Implementation specific**:
  * Not widely used
  * Listed here to avoid conflicts between implementations

## Known Flow Tags

### created_by

Status: **Deprecated**

Replaced by the `created_by` field in Flow metadata.
A string label identifying the entity which created the Flow.

### creation_date

Status: **Deprecated**

Replaced by the `created` field in Flow metadata.
Contains the ISO formatted date-time when a Flow was created.

### flow_status

Status: **Proposed**

Proposed in [ADR0006 - Flow Update Status](../adr/0006-flow-status.md).

Signals the current status of a Flow.

**NOTE:** Because these tags are maintained updated by a service other than the TAMS store, the value of this tag is only indicative and not authoritative.
If the service ingesting the content becomes unavailable, it may leave this tag in an incorrect state.
Services should aim to tidy up this state appropriately once they recover.

Known values:

* `awaiting_content` - Flow is expecting, but not currently receiving content
* `ingesting` - Content is currently being ingested
* `replication_in_progress` - Content is currently being ingested to this flow from another store via a replication process
* `closed_complete` - Flow is complete and will not receive any more content

### originating_id

Status: **Proposed**

Proposed in [ADR0004a - Flow and Source References](../adr/0004a-ancestry-relationships.md).

Used when this Flow was created by reference (i.e. this Flow is composed of pre-existing Segments in another Flow).
Contains the ID of the originating Flow.

### originating_timerange

Status: **Proposed**

Proposed in [ADR0004a - Flow and Source References](../adr/0004a-ancestry-relationships.md).

Used when this Flow was created by reference (i.e. this Flow is composed of pre-existing Segments in another Flow).
Contains the timerange in the originating Flow that corresponds to this flow.

### proxy_of_flow

Status: **Deprecated**

Used where this Flow is a proxy of another Flow.
Contains the ID of the Flow this is a proxy of.
Deprecated in favour of discovery via Flows of the same Source with appropriate metadata (e.g. lower generation, appropriate resolution, etc).

### input_quality

Status: **In use**

A human readable string identifying the quality of the media.

Known values:

* `intermediate` - i-frame only
* `contribution` - long-GOP
* `web` - long-GOP, low bit-rate

### salmon_created_by_job

Status: **Implementation specific**

Used by BBC R&D's experimental internal stream ingest service named "Salmon".
Records the Salmon job ID which created the Flow.

### writing_flow_timing_temi_timestamps

Status: **Implementation specific**

A boolean signalling that this Flow includes TEMI timing in MPEG-TS.
The media's timestamp is stored in the ptp_timestamp property in the TEMI Timeline Descriptor.

### \_cloudfit_squirrel_segmentation_rate

Status: **Implementation specific**

Used in BBC R&D's experimental internal TAMS implementation named "Squirrel".
A string representation of a Fraction, used to set the segment rate (segments per second) of the Flow.
This is an average rate.
Actual segment rates/durations may vary.

### \_tams_segmentation_rate

Status: **Implementation specific**

A string representation of a Fraction, used to set the segment rate (segments per second) of the Flow.
This is an average rate.
Actual segment rates/durations may vary.

### c2pa-provenance

Status: **Proposed**

Proposed in [APPNOTE0011 - C2PA provenance across related Sources and Flows](../appnotes/0011-c2pa.md).

Signals the presence of C2PA provenance data (a "manifest store") in a Flow or child Flow.

Known values:

* No Tag: A C2PA manifest has not been identified in this Flow
* `none`: A C2PA manifest is not present inside this Flow
* `embedded`: A C2PA manifest is present inside this multi-essence Flow
* `detached`: A C2PA manifest has been copied from this multi-essence Flow into a collected mono-essence data Flow.
  The Flow will have the role `c2pa` in the multi-essence Flow's `flow_collection` array.

### hls_segments

Status: **Experimental**

Used in the TAMS demonstration at IBC 2024.

The type is a `number`.
It is used to limit the number of segments presented in the HLS manifest.
Defaults to `150` if the tag is not set.
Use the value `inf` to list all segments.
However, listing all segments may result in the generation of the HLS manifest timing out.

### hls_segment_length

Status: **Experimental**

Used in the TAMS demonstration at IBC 2024.

The type is a `number`.
It is used to calculate the [MEDIA-SEQUENCE](https://datatracker.ietf.org/doc/html/rfc8216#section-4.3.3.2) value in the HLS manifest.
This tag is only used if the [flow_status](#flow_status) tag value is `ingesting`.
The value of this tag should be set to the duration of each segment in the flow (in seconds).
Flows using this feature must therefore have segments of consistant length.

### authz_class.${classname}

Status: **Experimental**

Suggested as a way to build lightweight Attribute-based Access Control in [AppNote0016: Authorisation in TAMS workflows](./0016-authorisation-in-tams-workflows.md).
The tag would actually be created once for each "class" associated with a Flow: for example there could be an `authz_class.news = 1` and `authz_class.sport = 1`.
As a result, queries can be constructed on the presence of specific tags, which would not be possible if it were a comma-seperated list for example `authz_class = news, sport`.
The value has no particular meaning, but tags must have a value.

No known implementations yet.

## Known Source Tags

There are currently no known Source Tags.
