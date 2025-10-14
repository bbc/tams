---
status: "proposed"
---
# Make `label` Mandatory for Uncontrolled Object Instances

## Context and Problem Statement

In [ADR0038](./0038-improved-storage-management.md), we added endpoints under `/objects` to facilitate the management of multiple Object Instances.
Since accepting that ADR, we have received feedback that `label` being optional for uncontrolled Object Instances makes it unclear how such Object Instances should be managed.
This ADR seeks to remedy that by making `label` mandatory when registering new uncontrolled Object Instances.

## Considered Options

* Option 1: Leave `label` as optional when registering uncontrolled Object Instances
* Option 2: Make `label` mandatory when registering uncontrolled Object Instances

## Decision Outcome

Chosen Option 2: Make `label` mandatory when registering uncontrolled Object Instances

### Implementation

Implemented by <https://github.com/bbc/tams/pull/155>

## Pros and Cons of the Options

### Option 1: Leave `label` as optional when registering uncontrolled Object Instances

* Neutral, because this avoids a breaking change to a lesser used part of the API
* Bad, because mechanisms for managing uncontrolled Object Instances without labels are undefined, because there is no natural key by which to identify a particular Object Instance - for example `DELETE /objects/{objectId}/instances` requires a label (or storage ID)

### Option 2: Make `label` mandatory when registering uncontrolled Object Instances

* Good, because mechanisms for managing all Object Instances will be defined
* Neutral, because this is a breaking change to a lesser used part of the API that will be released alongside the existing changes to Object management mechanisms
