---
status: "proposed"
---
# Flow Update Status

## Context and Problem Statement

Flow readers, and media players in particular, operate in different modes based on whether the Flow content they are consuming is expected to be updated or not. A Flow could be in the updating status because a non-realtime file ingest has not yet completed or a Flow is being ingested from a realtime stream that is still live.

The current design includes the `metadata_updated` and `segments_updated` Flow properties that contain the last metadata update date-time and last segment update date-time.
The Flow update status can currently be decided based on whether the time difference with the current system time is above or below a set time threshold.

## Decision Drivers

* Balance providing useful features and avoiding complexity in the TAMS design

## Considered Options

* Option 1: Use the Flow update properties to determine the Flow update status
* Option 2: Add a boolean `is_closed` property to explicitly indicate the Flow update status
* Option 3: Also state that the `is_closed` property can only be set once

## Decision Outcome

TBD

### Implementation

TBD

## Pros and Cons of the Options

### Option 1: Use the Flow update properties to determine the Flow update status

This is the current state of TAMS which includes the `metadata_updated` and `segments_updated` Flow properties.

* Good, it tracks actual updates rather than opinions from potential Flow updaters
* Bad, because the update status is decided for all Flows using a somewhat arbitrary and possibly "worst-case" time threshold

### Option 2: Add a boolean `is_closed` property to explicitly indicate the Flow update status

This extends option 1 to add a boolean `is_closed` to allow Flow updaters / managers to explicity indicate that the Flow is complete and is not expected to be updated in future.

* Good, because the Flow update status can be determined before the time threshold is reached
* Good, because it may also be useful when Flows have large update time gaps where `is_closed` is changed multiple times
* Bad, because the Flow update status might have to be changed in future, e.g. to fix something or the Flow status was set incorrectly, and Flow consumers may not be expecting that

### Option 3: Also state that the `is_closed` property can only be set once

This extends option 2 to only allow `is_closed` to be set to `true` once.

* Good, because once the Flow update status is set to closed it will never change
* Bad, because the Flow might need to be updated in future, e.g. to fix something or the Flow status was set incorrectly, and that won't be possible without resorting to copying the Flow to a new Flow
