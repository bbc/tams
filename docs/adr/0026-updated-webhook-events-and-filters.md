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
* Option 2a: Make the event filter and complete Flow Segment information requested by users
* Option 2b: Extend option 2a to add support for filtering by Source Collections
* Option 3: Make the event transformation updates requested by users

## Decision Outcome

Chosen option: Option 2b, because that provides most of what users have explicitly requested.
Also, filtering on Source Collections is likely to be needed in systems that operate on Sources.
The assumption is that the extra queries to get the Flow and Source Collection IDs is worth the benefits of having more advanced event filtering on collections.

Option 3 requires additional event processing to transform events for webhook endpoints.
It is unclear whether the additional processing warrants specification at this time.

There may be other ways to achieve a requirement to include or not include presigned `get_urls` in Flow Segments.

* A TAMS implementation may include a configure option to enable inclusion of presigned URLs.
* A Flow tag may be used to indicate where Flow Segment events should include presigned URLs.
An application that requires presigned URLs for performance reasons (e.g. to avoid an API request) can decide to enable it for the Flows it creates.
A permissions system sitting in front of a TAMS could decide whether users can enable presigned URLs for Flows using the tag.

### Implementation

Specification changes have been implemented in PR [#105](https://github.com/bbc/tams/pull/105).

## Pros and Cons of the Options

### Option 1: Leave the webhook specification unchanged

* Good, because it avoids making breaking changes to the specification
* Good, because it has been proven to work using existing implementations
* Bad, because it doesn't fulfill known user requirements which may lead to future divergence in implementations to meet those requirements

### Option 2a: Make the event filter and complete Flow Segment information requested by users

The `flow_ids` and `source_ids` filter option in the webhook registration now refer to just the Flow and/or Source entity directly associated with the event.
The Flow and Flow Segment events have a Flow (Flow `id` property) and Source (Flow `source_id` property) directly associated with it.
Note that the Flows and Sources could be collection Flows and Sources.

The `flow_collected_by_ids` filter option in the webhook registration refers to the Flow Collections referenced through the Flow `collected_by` property.

The `flows/segments_added` event is changed to add a `segments` property and remove the `timerange` property.
The `segments` property that contains a list of Flow Segment data structures that contain the same information as returned by the segments API endpoint.
Note that a TAMS implementation may limit the information returned in events, e.g. omit the presigned `get_urls` for security reasons.

The `timerange` property is removed from the `flows/segments_added` event as that information is now available in the union of `timerange` properties in the `segments`.

* Good, because it fulfills the known user requirements
* Good, because it extends the current specifiction rather than being a complete overhaul
* Neutral, because it requires an extra query to get the Flow Collection IDs (Flow's `collected_by` property) associated with the Flow
* Neutral, because more information is included in Flow Segment events which may increase the transmission and processing costs
* Neutral, because including presigned URLs in the Flow Segment information may compromise security as the webhook receiver is not directly involved in the authentication process

### Option 2b: Extend option 2a to add support for filtering by Source Collections

A system that prefers dealing with Sources rather than Flows would benefit from the ability to filter events based on Source Collections.
A filter based on Source Collections would also support additions to the underlying Flows without requiring the webhook to be re-registered with an updated list of Flows to filter on.

The `source_collected_by_ids` filter option is added to the webhook registration.
The property lists the Source Collections that collect the Source in the `collected_by` property.
The Source in the Flow and Flow Segment event case is the Source referenced by the Flow's `source_id` property.

* Good, because it provides a filtering capability at the Source level
* Good, because new Flows or Sources in a collection wouldn't require changes to the webhook registration
* Neutral, because it requires an extra query to get the Source Collection IDs (Source's `collected_by` property) associated with the Flow's Source

### Option 3: Make the event transformation updates requested by users

The webhook options could be extended with a `accept_get_urls` property that functions the same way as the query parameter on the segment access API endpoint.
This requires the event processing pipeline to transform the `segments` in the Flow Segment events by filtering the Flow Segment `get_urls` using the value set in `accept_get_urls`.

A `segment_timerange_only` webhook option could be used to reduce the size of Flow Segment events by returning just a `timerange` rather than the `segments`.

* Good, because it provides some control to webhook users of how much information is sent, which may help reduce transmission and processing costs.
* Bad, because it requires additional processing in the event transmission pipeline to transform the events

## More Information

### Event filter logic

The `events` webhook property lists the event types that are passed through the filter.
The `events` cannot be empty as an empty events is used to delete the webhook.

If `flow_ids` is set then Flow and Flow Segment events are only passed through if they refer directly to a Flow in the `flow_ids` list.
The `flows_ids` has no filter effect if not set or for Source events.

If `source_ids` is set then Flow, Flow Segment and Source events are only passed through if they refer directly to a Source in the `source_ids` list.
The `source_ids` has no filter effect if not set.

If `flow_collected_by_ids` is set then Flow and Flow Segment events are only passed through if they are `collected_by` a Flow Collection in the `flow_collected_by_ids` list.
The `flow_collected_by_ids` has no filter effect if not set or for Source events.

If `source_collected_by_ids` is set then Flow, Flow Segment and Source events are only passed through if they collected by a Source Collection in the `source_collected_by_ids` list.
The Flow is collected by a Source Collection if the Source referenced by the Flow is collected by the Source Collection.
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
