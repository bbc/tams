---
status: "rejected"
---
# Add created metadata to segments

## Context and Problem Statement

Within the current TAMS metadata model both the source and flow levels have metadata fields which track when the entities were created and who created them.
The segment level however does not have this information available and this can cause issues when trying to investigate the behaviour of a store.

With the current multi-store work and looking at content federation and replication then it would be useful to store this information at the segment level.
This data would also prove useful when analysing other workflows such as limited connectivity when segments are written out of order, or to analyse the speed of workflows such as proxy creation.


## Considered Options

* Option 1: Add new metadata fields to segment model
* Option 2: Do not change the API and manage separately

## Decision Outcome

tbc

### Implementation

See the API specification changes in PR [#xxx](https://github.com/bbc/tams/pull/xxx)

## Pros and Cons of the Options

### Option 1: Add new metadata fields to segment model

Add the created and created_by metadata fields to the segments data model to track when the segments are registered with the TAMS API.
This would follow the same model as for flows and sources and be optional fields with the same model for how they are created and managed.
Since segments are immutable then it is not proposed to include any form of updated fields within the data model.

- Good: Allows better tracking of segment content creation
- Bad: Additional metadata fields to be returned as part of the segment response that will not be needed for regular use cases.

### Option 2: Do not change the API and manage separately

The alternative option is to not change the TAMS API specification, but look at other methods of tracking segment creation outside the API.
This could take the form of analytics utilising either the webhook event notifications or implementation logging.

- Good: Minimises changes to the TAMS API
- Good: Keeps the segment response 
- Bad: Adds complexity to the system to find out basic information