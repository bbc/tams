---
status: "accepted"
---
# Flow Update Status

## Context and Problem Statement

Flow readers, and media players in particular, operate in different modes based on whether the Flow content they are consuming is expected to be updated or not.
A Flow could be in the updating status because a non-realtime file ingest has not yet completed or a Flow is being ingested from a realtime stream that is still live.

The current design includes the `metadata_updated` and `segments_updated` Flow properties that contain the last metadata update date-time and last segment update date-time.
The Flow update status can currently be decided based on whether the time difference with the current system time is above or below a set time threshold.

## Decision Drivers

* Balance providing useful features and avoiding complexity in the TAMS design

## Considered Options

* Option 1: Use the Flow update properties to determine the Flow update status
* Option 2: Add a boolean `is_closed` property to explicitly indicate the Flow update status
* Option 3: Also state that the `is_closed` property can only be set once

## Decision Outcome

Chosen option: Option 1: Use the Flow update properties to determine the Flow update status.

Clients will need to implement some kind of back off algorithm to decide how often to refresh the Flow extents.
As noted in [More Information](#tamsaws-workshop-discussion---13th-february-2024) section, this may be revisted in a future proposal that may include signalling of a flow status.

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

## More Information

### TAMS/AWS Workshop Discussion - 13th February 2024

A discussion about this proposal took place during the TAMS/AWS workshop on 13th February 2024, with the BBC R&D TAMS team, BBC B&EUT architects and AWS Solution Architects.

The discussion considered that there are two principles conflated in this concept: whether a Flow is still being created by some process (e.g. an `ingest_active` flag), and whether it is editorially complete.
The former is useful to understand whether a reader should poll the Flow extents to see if it can read more content, but is difficult to manage if the ingester fails and recovers, for example.
No compelling use cases were identified for the other case.

For this reason, Option 1 (checking the last update time) was chosen, and assumes clients will implement some kind of back off algorithm to decide how often to refresh the Flow extents.

In addition, there are other states a Flow could be in, for example existing as a placeholder for future content, or awaiting replication from another store.
This can be signalled with a tag, for example `flow_status`, which could be one of `awaiting_content`, `ingesting`, `replication_in_progress` or `closed_complete`, providing a non-authoritative hint to clients.
This will be added to a future Application Note describing known tags.
As in [Flow and Source References](https://github.com/bbc/tams/blob/main/docs/adr/0004a-ancestry-relationships.md), the TAMS team will monitor the use of tags, and revisit this proposal as needed.
