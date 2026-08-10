---
status: "accepted"
---
# Support for Fine-Grained Authorisation on Storage Backends

## Context and Problem Statement

[ADR0035](../adr/0035-fine-grained-auth.md) defined our approach to fine-grained authorisation in TAMS.
[AppNote0016](../appnotes/0016-authorisation-in-tams-workflows.md) describes how this may be implemented in practice.
The AppNote0016 approach relies upon the use of tags in key base resources.
[ADR0032](../adr/0032-specifying-storage-backend.md) added support for multiple Storage Backends.
But the lack of tags, or other appropriate metadata, limits the ability to apply AppNote0016 fine-grained auth to Storage Backends.

Deployers/implementers of TAMS have expressed desire for the ability to use fine-grained auth approaches with Storage Backends.
Use cases include cost allocation, cost management, and read only Storage Backends.

This ADR discusses the options for supporting fine-grained auth on Storage Backends.

## Considered Options

* Option 1: No change
* Option 2: Advise out-of-band authorisation for Storage Backends
* Option 3: Add read-only tags to Storage Backends
* Option 4: Add read-write tags to Storage Backends
* Option 5: Add an auth-specific parameter to Storage Backends

## Decision Outcome

Chosen Option 3: Add read-only tags to Storage Backends, because it matches existing patterns for fine-grained Auth and Storage Backend endpoints.

### Implementation

Implemented in [PR #229](https://github.com/bbc/tams/pull/229)

## Pros and Cons of the Options

### Option 1: No change

This option would maintain the current position with no changes to the API specification, or Application Notes.

* Good, because no changes are required in the specification
* Bad, because fine-grained auth would not be explicitly supported for Storage Backends
* Bad, because fragmented, non-standardised approaches to fine-grained auth for Storage Backends could emerge

### Option 2: Advise out-of-band authorisation for Storage Backends

This option would see no changes to the API specification, but an explicit recommendation in AppNote0016 that out-of-band methods should be used to implement/signal Storage Backend authorisation

* Good, because no changes are required in the specification
* Good, because fine-grained auth would be explicitly supported for Storage Backends
* Bad, because fragmented, non-standardised approaches to fine-grained auth for Storage Backends could emerge
* Bad, because it doesn't match existing patterns for auth

### Option 3: Add read-only tags to Storage Backends

This option would see tags added to Storage Backends, but no PUT/POST methods would be provided to set them via the API.
Instead, they would be set at deploy-time as with other existing Storage Backend parameters.
AppNote0016 would be updated to use the same patterns used for other resource types.

* Good, because fine-grained auth would be explicitly supported for Storage Backends
* Good, because it would produce a well-defined standard approach to Storage Backend auth
* Good, because it matches existing patterns for auth
* Neutral, because non-breaking changes are required in the specification
* Neutral, because changing of auth classes (or other tags) would require a re-deploy of the TAMS Service Implementation
  * Though use cases for frequent updating of these parameters are unclear

### Option 4: Add read-write tags to Storage Backends

As with Option 3, but with additional HTTP methods allowing CRUD operations on Storage Endpoint tags.

Good/Neutral/Bad as per Option 3, with the last point replaced by:

* Neutral, because changing of auth classes (or other tags) wouldn't require a re-deploy of the TAMS Service Implementation
  * Though use cases for frequent updating of these parameters are unclear
* Bad, because additional CRUD logic, and associated methods and storage would be required to manage these tags

### Option 5: Add an auth-specific parameter to Storage Backends

This option would see an auth-specific parameter added to Storage Backends.
AppNote0016 would be updated to use the same patterns used for other resource types but referencing this new parameter instead of tags.

* Good, because fine-grained auth would be explicitly supported for Storage Backends
* Good, because it would produce a well-defined standard approach to Storage Backend auth
* Neutral, because non-breaking changes are required in the specification
* Bad, because it doesn't match existing patterns for auth
