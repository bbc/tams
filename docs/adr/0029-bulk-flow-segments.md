---
status: "draft"
---
# Ability to bulk create flow segments

## Context and Problem Statement

As part of the work on [ADR0024 source level edit](https://github.com/bbc/tams/blob/main/docs/adr/0024-source-level-edit.md) (also known as edit by reference) it was identified that it could be useful to be able to bulk create flow segments within the API.
This ADR explores the impact of [option 5](https://github.com/bbc/tams/blob/main/docs/adr/0024-source-level-edit.md#option-5-provide-an-endpoint-to-bulk-write-flow-segments) on the API implementation.

When copying sections of one flow to another currently it is possible to query the TAMS API by time range and retrieve all the segments for a given flow.  
However to then write these to the new flow it requires a single API call to create each segment which is a considerable overhead when all the segments are know in advance.

One challenge is that in the current API specification the segments endpoint (`/flows/{flowId}/segments`) is already plural however only accepts the creation of a single segment.  

## Considered Options

- Option 1: Update existing flow segments endpoint to supply multiple segments
- Option 2: Create new bulk segments end point
- Option 3: Rename existing segments end point and create new bulk endpoint
- Option 4: Allow existing end point to support single and multiple segments
- Option 5: Do nothing

## Decision Outcome

Chosen option: "Option 4: Allow existing segments end point to accept both"
This was clearly the preferred option as it does not break existing API functionality, while remaining consistent with naming of other end points in the API.
Implementation is expected to not be significant within the API to look for a single or multiple segments.

### Implementation

## Pros and Cons of the Options

### Option 1: Update existing end point

Update the `POST /flows/{flowId}/segments` to always take an array of segments using the current data structure for each segment.  
For existing solutions this would require a change to wrap the single segment data in an array.

- Good - keeps the API very simple
- Bad - breaking change to the API
- Bad - requires all existing ingest solutions to be updated

### Option 2: Create new bulk segments end point

Create a new end point, eg `/flows/{flowId}/bulk_segments` to take an array of segments.

- Good - does not break existing implementations
- Bad - adds additional complexity to the API and implementation
- Bad - semantics suggests the segments end point should cope with multiple, so could cause confusion between the two end points

### Option 3: Rename existing segments end point and add bulk

Rename the existing `/flows/{flowId}/segments` to be singular `/flows/{flowId}/segment` and then replace the existing `/flows/{flowId}/segments` with the bulk end point

- Good - tidies up the existing semantics so the singular and pural end points match the functionality
- Bad - breaking change to API
- Bad - requires all existing ingest solutions to be updated
- Bad - adds additional complexity to the API and implementation

### Option 4: Allow existing segments end point to accept both

Update the existing `/flows/{flowId}/segments` to accept both the existing dict definition of a single segment as well as an array of segments

- Good - does not break the existing API
- Good - keeps the number of end points down
- Bad - adds some complexity to the API implementation

### Option 5: Do nothing

Leave the existing functionality in place

- Good - does not break the API
- Bad - requires implementors of edit by reference, or any bulk segment workflows, to call API for each segment
