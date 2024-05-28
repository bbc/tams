---
status: "accepted"
---
# Add Object Checksums and Filesizes

## Context and Problem Statement

TAMS clients need to have confidence in the integrity of media, that it has been transferred without corruption, and that the file transferred is the one that is expected.

Common methods of achieving this are `filesize` and `checksum` metadata.
Filesize provides a very basic method of verifying the file.
Is it the length that is expected?
Has the full file been transferred?
Checksums provide are slightly more expensive computationally, but provide a more reliable method of validating the file.
Cryptographically, is the file highly likely to be identical to the expected file.

This ADR considers if `filesize` and `checksum` metadata should be added to the TAMS API.

## Decision Drivers

* Provide high confidence in file integrity
* Provide a detection method for unauthorised/malicious file tampering

## Considered Options

* Option 1: Provide metadata fields for `filesize` and `checksum` which are populated by the client on write
* Option 2: Require TAMS implementations to calculate and populate these fields on write
* Option 3: Rely on existing `filesize` and `checksum` functionality in storage layers such as AWS S3

## Decision Outcome

Chosen option: Option 3: Rely on existing `filesize` and `checksum` functionality in storage layers such as AWS S3

Duplicating functionality/metadata that is already provided in the storage layer adds additional complexity for minimal benefit.
The risks alternatives address may be mitigated by implementing appropriate access control in deployed TAMS-compatible stores.

We may wish to produce an application note describing an example security model for TAMS-compatible stores.

We may wish to produce an application note describing how to verify file integrity using existing mechanisms in storage systems such as AWS S3.
Including a recommendation that clients SHOULD verify the integrity of uploaded segments, before registering them with the TAMS API.

## Pros and Cons of the Options

### Option 1: Provide metadata fields for `filesize` and `checksum` which are populated by the client on write

* Good, because its simple to implement
* Good, because it provides a means to verify objects have not been maliciously tampered with
* Neutral, because TAMS does not allow modification of existing objects
  * [ADR 0011](./0011-random-storage-object-ids.md) mitigates against malicious actors crafting requests which would create pre-signed PUT URLs for existing segments by requiring requests for new PUT URLs to return random object IDs
* Neutral, because proper securing of deployments mitigates, and detects the class of attacks this option mitigates
* Bad, because the class of malicious actions this option mitigates against (back-channel attacks) may also be targeted at the database storing the metadata fields
* Bad, because it potentially presents a new class of attack where the `filesize` or `checksum` are modified to make the data look invalid

### Option 2: Require TAMS implementations to calculate and populate these fields on write

* Good, because it provides a means to verify objects have not been maliciously tampered with
* Neutral, because TAMS does not allow modification of existing objects
  * [ADR 0011](./0011-random-storage-object-ids.md) mitigates against malicious actors crafting requests which would create pre-signed PUT URLs for existing segments by requiring requests for new PUT URLs to return random object IDs.
* Neutral, because storage backends such as S3 already provide mechanisms to calculate/check checksums/filesizes, which may be used to validate uploaded/downloaded files
* Neutral, because proper securing of deployments mitigates, and detects the class of attacks this option mitigates
* Bad, because it would require a change in architecture such that the TAMS API proxies file uploads such that it may calculate filesizes/checksums itself, or obtain these values from the storage layer
  * This increases complexity, and may negatively impact the scalability of the architecture
* Bad, because the class of malicious actions this option mitigates against (back-channel attacks) may also be targeted at the database storing the metadata fields
* Bad, because it potentially presents a new class of attack where the `filesize` or `checksum` are modified to make the data look invalid

### Option 3: Rely on existing `filesize` and `checksum` functionality in storage layers such as AWS S3

* Good, because it requires no additional complexity in the TAMS API or its implementations
* Good, because it still allows for verification of data at storage using existing mechanisms
* Good, because it provides no additional attack surface
* Neutral, because it relies on existing security methods for preventing/detecting malicious attacks on data
