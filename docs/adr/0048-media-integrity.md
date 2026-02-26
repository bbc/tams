---
status: "proposed"
---
# Integrity model for media in TAMS, and when interacting with other systems

## Context and Problem Statement

When using TAMS for archiving of content, or when TAMS interacts with other archive systems, ensuring integrity of media is of particularly high priority with different considerations to short and medium term applications.
Checksums are commonly used in archives to ensure the integrity of assets.

This ADR covers decisions made in the creation of Application Note 0021 - Integrity model for media in TAMS, and when interacting with other systems.


## Decision Drivers

* Integrate with existing integrity features of underlying systems where possible
* Support integration with existing archival file integrity approaches
* Support both file-like and live-like workflows
* Avoid breaking existing workflows

## Considered Options

* Option 1: Rely entirely on the durability of subsystems
* Option 2: Allow passthrough of existing checksum support in storage backends
* Option 3: Store Object checksums in Flow metadata
* Option 4: Store "whole Flow" data-level checksum in Flow metadata
* Option 5: Store "whole Flow" checksum of checksums in Flow metadata
* Option 6: Store list of checksum of checksums in Flow metadata
* Option 7: Store checksum of checksums in separate Flow

## Decision Outcome

Chosen options 2,and 7.

This combination would allow end-to-end checksums to be stored in the Object store against a single-segment Flow.
A chunked variant may then be provided against a separate Flow with the same Source.
The sequence of Segments in the chunked Flow may then be protected via a checksum-of-checksums.

The only spec alteration would be to call out that implementations should not stand in the way of existing checksum mechanisms of the products advertised for a given Storage Backend.

### Implementation

Implemented in [PR #176](https://github.com/bbc/tams/pull/176).

## Pros and Cons of the Options

### Option 1: Rely entirely on the durability of subsystems

This option would see the existing status-quo remain.
The probabilities of data loss/corruption would be presented in an Application Note.
But no further changes would be made.

* Good, because it requires no changes to the spec
* Good, because the calculated probabilities of loss have been calculated to be acceptable for many deployments
* Bad, because it precludes the use of existing archival best practice of end-to-end checksums

### Option 2: Allow passthrough of existing checksum support in storage backends

All major Object storage solutions provide a means of supplying a checksum for an Object in the header when uploading that Object.
This option would see recommendations that implementations allow/pass through those headers.

* Good, because it requires little/no changes to the spec
* Good, because it allows for the probability of loss/corruption to be further minimised
* Good, because it supports the use of existing archival best practice of end-to-end checksums
* Neutral, because while the integrity of individual objects is protected, the integrity of the sequence of those Objects isn't

### Option 3: Store Object checksums in Flow metadata

As with Option 2, but with checksums stored in Flow metadata instead of the native Object store solution.

* Good, because it is agnostic to Storage Backends
* Bad, because the checksum in Flow metadata will likely not be the one used in automated integrity checking
* Bad, because checksum is not stored with the data

### Option 4: Store "whole Flow" data-level checksum in Flow metadata

This would see a checksum of the data of the "whole Flow" stored in Flow metadata.

This option may be brittle.
Media in TAMS is commonly stored in a chunk form for flexibility and performance.
The process of chunking and re-combining media can be non-deterministic for many formats.
While the media may be bit-identical, the metadata in headers may not be.
Even where the metadata is identical, it's order may be different.
This would change the checksum of the media when re-combined into a "whole Flow".

Additionally, while there is a common tag to indicate when a Flow is "complete", the core data model assumes an infinite timeline which may be randomly read/written/delete at any point on that timeline.
This would make "whole Flow" checksums incompatible with many common TAMS workflows.

The calculation of a "whole Flow" checksum would also require the reading of all of the data in the Flow.
This would be inefficient when generating checksums following a streamed ingest, or when reading & validating a short section of a Flow.

* Good, this would be the end-to-end checksum in many cases
* Neutral, because it would require a spec change, or new tag
* Bad, because it would be unreliable for chunked media where the chunking/combining processes may be non-deterministic
* Bad, because it would only support file-like workflows
* Bad, because it requires the reading of all data in a Flow to calculate the checksum

### Option 5: Store "whole Flow" checksum of checksums in Flow metadata

As with Option 4, but the checksum would be a "checksum of checksums".
A "whole Flow" checksum would be calculated using the Object checksums.
This would mitigate the determinism issues with chunked media.

* Good, because it would be reliable for chunked media where the chunking/combining processes may be non-deterministic
* Neutral, because it would require a spec change, or new tag
* Neutral, because this checksum would not match existing end-to-end checksums
* Bad, because it would only support file-like workflows
* Bad, because it requires the reading of all object checksums in a Flow to calculate the whole Flow checksum

### Option 6: Store list of checksum of checksums in Flow metadata

As with Option 5, but each checksum-of-checksums would cover multiple Objects in a short section of the Flow.

This option would require a spec change as tags do not support dictionaries (which would be required for the pairing of timerange, and checksum-of-checksums), so this would require either additional tag capabilities or a new Flow parameter.

* Good, because it would be reliable for chunked media where the chunking/combining processes may be non-deterministic
* Good, because it would support all TAMS workflows
* Good, because it minimises data read to calculate checksums
* Neutral, because this checksum would not match existing end-to-end checksums
* Neutral, because it would require a spec change
* Bad, because the list of checksums in TAMS metadata may get very large

### Option 7: Store checksum of checksums in separate Flow

As with Option 6, but store the checksum-of-checksums in a Data Flow associated with the original Flow.

* Good, because it would be reliable for chunked media where the chunking/combining processes may be non-deterministic
* Good, because it would support all TAMS workflows
* Good, because it minimises data read to calculate checksums
* Good, because it wouldn't require a spec change
* Neutral, because this checksum would not match existing end-to-end checksums
* Neutral, because the small payload for each checksum Segment would be very small going against best practice
