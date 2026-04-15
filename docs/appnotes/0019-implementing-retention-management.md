# 0019: Methods of implementing retention management

This describes how to implement the automatic deletion of Flows and Segments.

## Segment Retention

This approach may be used to control the automatic deletion of Flow Segments.
Segment retention time may be signalled via the `segment_retention_offset` tag.
This tag provides an offset, formatted as a TAMS-compatible Timestamp, that should be applied to the end component of a Segment's TimeRange to calculate the time at which it should be deleted.

Note that a Flow's timeline might not use time of day.
But this mechanism can still be used to progressively delete Segments given an appropriate `segment_retention_offset`.

The execution of the deletion of Flow Segments may be carried out by the TAMS service instance itself, or a worker client.
In either case, the following should be considered:

* The `segment_retention_offset` may be adjusted up or down after having being set initially
* The system enacting the delete will need Delete permissions on the Flow
* The Flow Segments may be manually deleted by a client before the time configured for automated deletion
* There may be gaps between segments on the Flow's timeline

### Worker Client

Worker clients will initially need to populate their list of Flows which have Segment Retention configured.
This may be achieved by performing a GET to `/flows` with the query parameter `tag_exists.segment_retention_offset=true`.
This will retrieve a list of Flows and their metadata including tags required for this function.

Worker clients will also need to keep their internal list up to date.
This may be achieved with by regularly polling the API as above or by subscribing to the `flows/created`, `flows/updated`, and `flows/deleted` events via webhooks.
Where polling is used, a suitable interval should be chosen that balances the latency of the deletes and the number of requests made to the TAMS API.
Latency, in this case, would occur where the configured delete time is earlier than the first poll that would identify it.

In some cases, worker clients may wish to check for updates to relevant Flow metadata (i.e. via a GET to `/flows/<flow_id>`) before enacting a delete, to detect any changes to the delete time.
But due to the high number of delete requests associated with this process may make this impractical.

This simplest way to enact the Segment deletes is via regular DELETE requests to `/flows/<flow_id>/segments` with the `timerange` query parameter set to `_<calculated_timestamp>)` where `<calculated_timestamp>` is the TAI Timestamp for the current time minus the value of `segment_retention_offset`.
This method requires fewer API requests than deleting each Segment individually at it's scheduled delete time.
But it does result in a delay of up to the amount of time between delete requests.

Where minimal latency for deletes is required, a GET to `/flows/{flowId}/segments` shall return Segments and their timeranges which may be used to calculate their delete times.
Delete requests to `/flows/<flow_id>/segments` may then be performed at the appropriate time with `timerange` query parameter set to `_<calculated_timestamp>)` where `<calculated_timestamp>` is the end time of the Segment to be deleted.

## Flow Retention

This approach may be used to control the automatic deletion of Flows.
Flow retention time may be signalled via the `flow_retention_offset` tag.
This tag provides an offset, formatted as a TAMS-compatible Timestamp, that should be applied to the greater of the `metadata_updated` or `segments_updated` times of a Flow.
The resultant time is when the Flow should be deleted.

The execution of the deletion of the Flow may be carried out by the TAMS service instance itself, or a worker client.
In either case, the following should be considered:

* The `flow_retention_offset` may be adjusted up or down after having being set initially
* `metadata_updated` and `segments_updated` will be updated with a later datetime whenever the metadata or segments are updated respectively
* The system enacting the delete will need Delete permissions on the Flow
* The Flow may be manually deleted by a client before the time configured for automated deletion

### Worker Client

Worker clients will initially need to populate their list of Flows which have Flow Retention configured.
This may be achieved by performing a GET to `/flows` with the query parameter `tag_exists.flow_retention_offset=true`.
This will retrieve a list of Flows and their metadata including tags, `metadata_updated`, and `segments_updated` required for this function.

Worker clients will also need to keep their internal list up to date.
This may be achieved with by regularly polling the API as above or by subscribing to the `flows/created`, `flows/updated`, and `flows/deleted` events via webhooks.
Where polling is used, a suitable interval should be chosen that balances the latency of the deletes and the number of requests made to the TAMS API.
Latency, in this case, would occur where the configured delete time is earlier than the first poll that would identify it.

Worker clients should also check for updates to relevant Flow metadata before enacting a delete, to detect any changes to the delete time.
This may be achieved via a GET to `/flows/<flow_id>`.
The delete of a flow may be achieved via a DELETE to `/flows/<flow_id>`.
Deletes may be enacted at the specific time configured (e.g. by triggering via a cron job), or may be processed in batches within a reasonable period after the configured time (e.g. in the same process which polls the API for updates).

## Empty Flow Clean-up

This approach may be used to automatically remove empty Flows.
The execution of the deletion of empty Flows may be carried out by the TAMS service instance itself, or a worker client.
Either way, it should be configured directly with an offset much like the one used in regular Flow Deletion.

### Worker Client

Empty Flows may be located via a GET request to `/flows` with the `timerange` query parameter set to `()`, aka the "empty" Timerange.
Flows in the return data with both `metadata_updated` and `segments_updated` earlier than the current time minus the pre-configured offset should be deleted via a DELETE to `/flows/<flow_id>`.
