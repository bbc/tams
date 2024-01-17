---
status: "proposed"
---
# Expand Created-by and Modified-by Metadata

## Context and Problem Statement

The existing API definition provides a `created-by` metadata field in the flow metadata.
This field contains an identifier for the entity which originally created the flow.
A similar `created-by` field on flow deletion requests would be useful.
Additionally, a `modified-by` field in flow metadata to track the entity which most recently modified requests would also be useful.

## Decision Drivers

* It has been useful to track the entity which created flows, primarily as a debugging tool, and to query flows by the entity which created them
* Flows may be modified by entities other than the one that created the flow
* Debugging/querying of modifications of flows and creation of flow deletion requests is currently more difficult than debugging/querying creation of flows

## Considered Options

* Provide additional metadata fields within the TAMS API
* Only store this information in other systems (e.g. AAA systems), outside of the scope of TAMS

## Decision Outcome

Chosen option: "Provide additional metadata fields within the TAMS API", because
This has been identified as a highly useful capability which should be available in a minimal system (i.e. one where only a TAMS service is deployed)

### Implementation

Implemented by https://github.com/bbc/tams/pull/17

## Pros and Cons of the Options

### Provide additional metadata fields within the TAMS API

* Good, because it reduces the barrier to deploying a minimal TAMS service Vs. the alternative
* Neutral, because it doesn't prevent the use of AAA systems
* Bad, because it may result in duplication of metadata in AAA systems

### Only store this information in other systems

* Good, because other systems such as AAA systems often provide more granular/extensive metadata
* Bad, because other systems such as AAA systems can be relatively difficult/complicated to set up
* Bad, because it necessitates the use of a further service for a fundamental capability
