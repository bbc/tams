---
status: "proposed"
---
# Updated Webhook Events and Filters

## Context and Problem Statement

TAMS includes an endpoint to register webhooks for receiving Flow, Flow Segment and Source events.
The API specification for the webhook was intended to provide an example of a basic webhook with filtering capabilities.
It was assumed that developers would implement and use the basic webhook that is available in implementations and that later iterations of the TAMS specification would incorporate changes based on learnings and to better match real-world requirements.

The webhook as specified was found to be useful to users of the current set of TAMS implementations, but they have asked for some updates.
This ADR proposes some updates to the webhook specification in TAMS.

## Decision Drivers

* Users have asked to filter on Flow Collections such that all events associated with Flows in the collection are included.
This avoids needing to query the list of Flows in the collection when registerering the webhook.
This allows new Flows to be added to the collection without requiring a new webhook with updated filters to be registered, avoiding disruption to the event streams.
* Users have asked to be able to filter Flow and Flow Segment events by Source ID.
* Similar to filtering on Flow Collection, it would be useful to be able to filter Flow and Flow Segment events by Source Collections as well.
* Users have asked to have the Flow Segment events contain the same information that is present in the API endpoint response.
This avoids needing additional API queries to get the missing information.
* Users have asked to be able to filter the `get_urls` in Flow Segments in the same way that is currently possible in API endpoint requests.

## Considered Options

* Option 1: Leave the webhook specification unchanged
* Option 2: Make the event filter and complete Flow Segment information requested by users
* Option 3: Extend option 2 to add support for filtering by Source Collections
* Option 4: Extend option 3 to add filtering of Flow Segment `get_urls`

## Decision Outcome

Chosen option: Option 4, because that provides what users have explicitly requested and filtering on Source Collections is likely to be needed in systems that operate on Sources.
The assumption is that the extra queries to get the Flow and Source Collection IDs is worth the benefits of having more advanced event filtering on collections.
Similarly, the event transformation capability to select which `get_urls` to include allows access to content to be limited for certain webhook event recipients that don't have the required permissions.

API implementations may choose to only partially support the filtering and transformation capabilities, but they must return a 400 HTTP error code response on registration if the requested webhook capabilities are not fully supported.
The avoids the scenario where for example webhook events include presigned URLs even though the API user has set `accept_get_urls` to an empty list because the webhook event recipient does not have permission to access the content.

### Implementation

Specification changes have been implemented in PR [#105](https://github.com/bbc/tams/pull/105).

## Pros and Cons of the Options

### Option 1: Leave the webhook specification unchanged

* Good, because it avoids making breaking changes to the specification
* Good, because it has been proven to work using existing implementations
* Bad, because it doesn't fulfill known user requirements which may lead to future divergence in implementations to meet those requirements

### Option 2: Make the event filter and complete Flow Segment information requested by users

The `flow_ids` and `source_ids` filter option in the webhook registration now refer to just the Flow and/or Source entity directly associated with the event.
The Flow and Flow Segment events have a Flow (Flow `id` property) and Source (Flow `source_id` property) directly associated with it.
Note that the Flows and Sources could be collection Flows and Sources.

The `flow_collected_by_ids` filter option in the webhook registration refers to the Flow Collections referenced through the Flow `collected_by` property.

The `flows/segments_added` event is changed to add a `segments` property and remove the `timerange` property.
The `segments` property that contains a list of Flow Segment data structures that contain the same information as returned by the segments API endpoint.
Note that a TAMS implementation may limit the information returned in events, e.g. omit the presigned `get_urls` for security reasons.

The `timerange` property is removed from the `flows/segments_added` event as that information is now available in the union of `timerange` properties in the `segments`.

See the [More Information](#more-information) section for filtering guidelines and use cases.

* Good, because it fulfills the known user requirements
* Good, because it extends the current specifiction rather than being a complete overhaul
* Neutral, because it requires an extra query to get the Flow Collection IDs (Flow's `collected_by` property) associated with the Flow
* Neutral, because more information is included in Flow Segment events which may increase the transmission and processing costs
* Neutral, because including presigned URLs in the Flow Segment information may compromise security as the webhook receiver is not directly involved in the authentication process

### Option 3: Extend option 2 to add support for filtering by Source Collections

A system that prefers dealing with Sources rather than Flows would benefit from the ability to filter events based on Source Collections.
A filter based on Source Collections would also support additions to the underlying Flows without requiring the webhook to be re-registered with an updated list of Flows to filter on.

The `source_collected_by_ids` filter option is added to the webhook registration.
The property lists the Source Collections that collect the Source in the `collected_by` property.
The Source in the Flow and Flow Segment event case is the Source referenced by the Flow's `source_id` property.

See the [More Information](#more-information) section for filtering guidelines and use cases.

* Good, because it provides a filtering capability at the Source level
* Good, because new Flows or Sources in a collection wouldn't require changes to the webhook registration
* Neutral, because it requires an extra query to get the Source Collection IDs (Source's `collected_by` property) associated with the Flow's Source

### Option 4: Extend option 3 to add filtering of Flow Segment `get_urls`

The webhook options is extended with a `accept_get_urls` property that functions the same way as the query parameter on the segment access API endpoint.
This requires the event processing pipeline to transform the `segments` in the Flow Segment events by filtering the Flow Segment `get_urls` using the value set in `accept_get_urls`.

* Good, because it provides some control to webhook users of how much information is sent, which may help reduce transmission and processing costs.
* Neutral, because it requires additional processing in the event transmission pipeline to transform the events that may be trivial or non-trivial depending on the implementation architecture.

## More Information

### Event filter guidelines

The events can be filtered by associated Flows, Sources, Flow Collections and Source Collections.
The following properties are needed by the filter process for Flow and Flow Segment events (the name used here is structured as `{entity}.{property}`):

* `Flow.id`: the ID of the Flow.
* `Flow.collected_by`: the IDs of the Flow Collections that collect the Flow.
* `Source.id`: the ID of the Flow's Source.
The property value equals `Flow.source_id`.
* `Source.collected_by`: the IDs of the Source Collections that collect the Flow's Source.

The following properties are needed by the filter process for Source events:

* `Source.id`: the ID of the Source.
* `Source.collected_by`: the IDs of the Source Collections that collect the Source.

The `events` webhook property lists the event types that are passed through the filter.
The `events` cannot be empty as an empty events is used to delete the webhook.

If the `flow_ids` webhook property is set then Flow and Flow Segment events are only passed through if the `Flow.id` is in the `flow_ids` list.
The `flows_ids` has no filter effect if not set or for Source events.

If the `source_ids` webhook property is set then Flow, Flow Segment and Source events are only passed through if the `Source.id` is in the `source_ids` list.
The `source_ids` has no filter effect if not set.

If the `flow_collected_by_ids` webhook property is set then Flow and Flow Segment events are only passed through if there is an ID in the `Flow.collected_by` list that is also in the `flow_collected_by_ids` list.
The `flow_collected_by_ids` has no filter effect if not set or for Source events.

If the `source_collected_by_ids` webhook property is set then Flow, Flow Segment and Source events are only passed through if there is an ID in the `Source.collected_by` list that is also in the `source_collected_by_ids` list.
The `source_collected_by_ids` has no filter effect if not set.

### Some use cases and associated webhook options

Here are some general use cases along with the webhook options:

* Allow users to filter which events types to receive
  * Set the `events` property to the list of event types to receive
* Allow users to filter Flow and / or Flow Segment events for a specific Flow
  * Set the `events` to include the Flow and / or Flow Segment event types as required
  * Add the Flow ID to the `flow_ids` property
* Allow users to filter Flow and / or Flow Segment events for all Flows of a Source
  * Set the `events` to include the Flow and / or Flow Segment event types as required
  * Add the Source ID to the `source_ids` property
* Allow users to filter Flow and / or Flow Segment events for all Flows collected by a Flow Collection
  * Set the `events` to include the Flow and / or Flow Segment event types as required
  * Add the Flow Collection ID to the `flow_collected_by_ids` property
* Allow users to filter Flow and / or Flow Segment events for a Flow Collection as well as all Flows collected by that Flow Collection
  * Set the `events` to include the Flow and / or Flow Segment event types as required
  * Add the Flow Collection ID to the `flow_ids` property
  * Add the Flow Collection ID to the `flow_collected_by_ids` property
* Allow users to filter Source events for a Source
  * Set the `events` to include the Source event types as required
  * Add the Source ID to the `source_ids` property
* Allow users to filter Source events for all Sources collected by a Source Collection
  * Set the `events` to include the Source event types as required
  * Add the Source ID to the `source_collected_by_ids` property
* Allow users to filter Source events for all Sources for a Source Collection as well as all Sources collected by that Source Collection
  * Set the `events` to include the Source event types as required
  * Add the Source Collection ID to the `source_ids` property
  * Add the Source ID to the `source_collected_by_ids` property
* Allow users to filter Flow and / or Flow Segment events for all Flows that have the Source collected by a Source Collection
  * Set the `events` to include the Flow and / or Flow Segment event types as required
  * Add the Source Collection ID to the `source_collected_by_ids` property
* Allow users to filter events for multiple Flows
  * Set the `events` to include Flow and / or Flow Segment event types as required
  * Add the Flow IDs to the `flow_ids` property
* Allow users to filter events for multiple Flow Collections
  * Set the `events` to include Flow and / or Flow Segment event types as required
  * Add the Flow Collection IDs to the `flow_collected_by_ids` property
* Allow users to filter events for multiple Sources
  * Set the `events` to include the event types as required
  * Add the Source IDs to the `source_ids` property
* Allow users to filter events for multiple Source Collections
  * Set the `events` to include the event types as required
  * Add the Source Collection IDs to the `source_collected_by_ids` property
* Allow users to disable `get_urls` inclusion in Flow Segments
  * Set the `accept_get_urls` to an empty list
* Allow users to only pass through certain `get_urls` in Flow Segments
  * Set the `accept_get_urls` to the list labels of URLs that should be included
