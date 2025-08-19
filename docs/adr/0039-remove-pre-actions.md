---
status: "proposed"
---
# Proposal to remove pre-actions from storage allocation responses

## Context and Problem Statement

Prior to the open-sourcing of the TAMS specification, a performance bottleneck was noticed on some HTTP Object Storage implementations.
When the number of objects in a bucket exceeded a certain value, there would be a multi-second delay to the processing of requests while the bucket was sharded.

This was initially mitigated by creating new buckets to limit the number of objects within any given bucket.
As there is no requirement for users to use all object IDs allocated to them, an approach to avoiding/handling unused/empty buckets was required.
The approach chosen was to provide pre-signed URLs that clients could use to create the buckets when they needed them.
These "pre-actions" are indicated in the `pre` section of the response body for the storage endpoint.

An alternative solution of "pre-sharding" buckets was eventually identified for the HTTP Object Storage service affected.
But the pre-actions were left in place to allow for similar issues to be addressed as and when they arose in other storage backends.

Since then, we have not identified any further need for pre-actions.
No known store implementation use them.

[ADR0034](https://github.com/bbc/tams/blob/main/docs/adr/0034-storage-allow-object_ids.md) added support for clients to specify Object IDs.
This was driven by use cases such as maintaining IDs when transferring content between stores.
The specifying of Object IDs by clients has the side affect that the existing method of identifying if a bucket must be created for the new object will not work.
As the bucket name used to identify if a pre-action should be executed is embedded in the Object ID.
This hasn't caused issues in practice because, as previously stated, no currently known implementations of TAMS services use pre-actions.

The lack of use of pre-actions in the real world presents an additional risk in that clients may not implement pre-actions correctly, or at all.
This could result in unexpected incompatibility between implementations.

## Decision Drivers

* Lack of implementation of pre-actions by services
* Lack of appropriate means to test that pre-actions are implemented correctly by clients
* Client-specified Object IDs may not work correctly on services which use pre-actions
* Lack of real-world use cases for pre-actions
  * The only known use case has alternative solutions that are arguably better

## Considered Options

* Option 1: No changes
* Option 2: Move bucket ID to a separate parameter
* Option 3: Remove pre-actions

## Decision Outcome

Chosen option 3: Remove pre-actions.
This will simplify the specification by removing a feature which is non-trivial to implement, but has no current real-world use cases.

### Implementation

{Once the proposal has been implemented, add a link to the relevant PRs here}

## Pros and Cons of the Options

### Option 1: No changes

This option would see the specification left as it is.

* Good, because it doesn't require breaking changes to the API
* Bad, because it means client-specified Object IDs may not work in all cases
* Bad, because clients have to parse Object IDs to identify bucket IDs which need pre-actions performing
* Bad, because it is currently difficult to ensure pre-actions are implemented correctly
* Bad, because it's a non-trivial part of the spec that we have no real use cases for

### Option 2: Move bucket ID to a separate parameter

This option would see pre-actions remain, but elevate bucket IDs to their own parameter in `put_urls`.

* Good, because it would allow pre-actions to be compatible with client-specified Object IDs
* Good, because it means clients don't have to parse Object IDs to identify buckets names for pre-actions
* Neutral, because its a breaking change to pre-actions workflows
* Bad, because it is currently difficult to ensure pre-actions are implemented correctly
* Bad, because it persists a non-trivial part of the spec that we have no real use cases for

### Option 3: Remove pre-actions

This option would see support for pre-actions removed from the storage endpoint.

* Good, because client-specified Object IDs will work in all cases
* Good, because extra information will no longer be embedded in Object IDs
* Good, because it removes a non-trivial part of the spec that we have no real use cases for
* Neutral, because it's a breaking change to pre-actions workflows that we don't believe are in any implementations
