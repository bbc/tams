---
status: "proposed"
---
# Signalling Retention Time

## Context and Problem Statement

It is common in media workflows to have a continuous ingest where media is only retained for a fixed period of time.
Such systems are commonly known as "Loop Recordings" or "Circular Buffers".
These systems are often used where storage is limited, or where the value of the media diminishes over time.
They may also be used as part of a workflow where valuable content is explicitly selected for longer term storage, with anything else being automatically deleted.
Or where media is transcoded or otherwise processed within a set window following capture/ingest.

Cloud-based object storage does afford greater flexibility in terms of the scale and duration for which media may be stored.
But such workflows are still useful to avoid the ongoing cost and resource use of storing media indefinitely.

TAMS' strong timing, support for short segments, and event mechanisms make implementing such features trivial.
Such functionality can even be implemented efficiently as a client of TAMS, rather than as a deeply integrated feature of the service.
An [open-source implementation](https://github.com/aws-samples/time-addressable-media-store-tools?tab=readme-ov-file#deploylooprecorder) is available in the AWS TAMS Tools repository.
This implementation uses a Flow tag with the name `loop_recorder_duration` which takes a duration in seconds.

Given the prevalence of these workflows, this ADR discusses if and how TAMS might explicitly support such functionality.

Firstly, some generally applicable discussion of how this feature may fit with the wider TAMS design.

The TAMS specification has always been tightly scoped as a media store API.
Its purpose is to facilitate the storage, retrieval, and advertisement of media.
It is often stated that "TAMS is not a MAM", referring to the complex features of a Media Asset Management system.
The assumption being that, for more complex use cases, a MAM layer may sit on top of a TAMS service.
Or a MAM may provide a TAMS API as an interoperable means to interact with the MAM at a basic level.
Loop recording could be consider a concern for another system, such as a MAM.

To judge this position, we might consider what other types of media management TAMS is currently responsible.

TAMS implementations are currently responsible for the reference counting of Media Objects and deleting the Objects from storage once it is no longer references by any Flow Segments.
It is vital for the management of Media Objects given that they have no conceptual "owner" within the TAMS system, and thus no other system responsible for their deletion.
This operation is performed by reference counting Object IDs as opposed to explicit signalling by the client.
It requires no configuration.
This is also a case where an instance may be considered to be performing its own maintenance routines.
Loop recording, on the other hand, may be configured via data in the TAMS Service (tags or a field in the core spec) but actually enacted by a secondary system.

Webhooks are an example where TAMS may be configured in a way that influences an external system.
But only in that they set where a stream of event data is to be sent, and what data will be included in that stream.
In that sense, it may be considered a form of the advertisement of data in a TAMS system rather than the explicit configuration of a system that modifies that data.

Webhooks are also an example of an optional feature in TAMS.
The availability of this feature on a given store implementation is advertised via the `event_stream_mechanisms` parameter on the `/service` endpoint.

The proposed approach to Fine-Grained Auth in TAMS is an example where configuration in TAMS (a list of groups with permissions on a TAMS resource) will be used to influence the behaviour of a non-core feature.
Fine-grained auth may be tightly integrated into a Service implementation or be implemented in a secondary service (i.e. an auth proxy).
This signalling will initially be implemented in tags.
Similar considerations about how to manage an optional feature apply to Fine-Grained Auth.

With this in mind, loop recording configuration would present a step beyond the types of functionality currently provided by the TAMS specification.

TAMS clients have shown that there is a desire to co-ordinate loop recording via metadata in TAMS.
But we should consider the implications of the options for doing so on implementations.
Should loop recording be an optional feature?
If so, how should the availability of that feature be advertised, if indeed it is advertised?
Should this feature be deeply integrated into TAMS, or should we expect that this feature continues to be provided by a secondary system?

In addition to loop recording, another desirable type of automated clean-up is the deletion of Flows at or after a period of time.
This ADR will also explore some options for such a feature.

## Considered Options

* Option 1: Leave loop recorder signalling up to the implementer
* Option 2: Explicitly make loop recording the responsibility of the client which would otherwise configure such a feature
* Option 3: Define a well known tag in the tags listing
* Option 4a: Define an optional parameter in the core specification, with support signalled
* Option 4b: Define an optional parameter in the core specification, with support not signalled
* Option 4c: Define an optional parameter in the core specification, with mandatory support
* Option 5a: Describe a method of deleting Segments after a period of time from their registration
* Option 5b: Describe a method of deleting Segments at a time offset from their TimeRange end
* Option 5c: Describe a method of deleting Segments to maintain a maximum duration for a Flow
* Option 6a: Describe a method of deleting an entire Flow at a specific time
* Option 6b: Describe a method of deleting an entire Flow at a time offset from its creation time
* Option 6c: Describe a method of deleting an entire Flow at a time offset from its Segments updated time
* Option 6d: Describe a method of deleting an entire Flow at a time offset from the most recent of Segments updated or Metadata updated time
* Option 7: Describe potential implementation architectures in an Application Note

## Decision Outcome

Chosen options:

* Option 3: Define a well known tag in the tags listing
* Option 5b: Describe a method of deleting Segments at a time offset from their TimeRange end
* Option 6d: Describe a method of deleting an entire Flow at a time offset from the most recent of Segments updated or Metadata updated time
* Option 7: Describe potential implementation architectures in an Application Note

This combination of options shall result in a clearly defined approach to implementing loop recording functionality.
It avoids adding any features to the core specification which cannot be relied upon at all times.
It avoids blurring the line between the core TAMS Service and wider ecosystem by communicating features potentially provided by that wider ecosystem via the core specification.
It does, however, require those deploying and using TAMS systems to know out-of-band what additional features (i.e. those beyond the core spec) are and aren't available for their use.

### Implementation

{Once the proposal has been implemented, add a link to the relevant PRs here}

## Pros and Cons of the Options

### Option 1: Leave loop recorder signalling up to the implementer

This option would see loop recorder signalling and functionality to be defined by the implementers.
TAMS would not define any specific signalling mechanism.

* Good, because it avoids a spec change
* Good, because it avoids adding a feature to the spec that would likely need to have optional support
* Bad, because it may result in fragmented compatibility around a common function

### Option 2: Explicitly make loop recording the responsibility of the writing client of loop recording Flows

This option would see loop recorder signalling and functionality to be defined by the implementers.
TAMS would not define any specific signalling mechanism.
TAMS would explicitly state that such functionality is the responsibility of the client writing loop recording Flows.

* Good, because it avoids a spec change
* Good, because it avoids adding a feature to the spec that would likely need to have optional support
* Good, because it provides clear guidance on responsibility for this feature
* Good, because it avoids fragmented compatibility around a common function
* Bad, because it couples writing and deleting responsibility in this case
* Bad, because it may require some organisations to use different ingest clients for different purposes

### Option 3: Define a well known tag in the tags listing

This option would see the signalling/configuration of the feature be via a well known Flow tag.

* Good, because it avoids a spec change
* Good, because it avoids adding a feature to the spec that would likely need to have optional support
* Good, because it avoids fragmented compatibility around a common function
* Good, because it does not make an assumption about where the feature would be implemented (i.e. in the service, or elsewhere)
* Neutral, because it avoids a proliferation of features in the core spec
* Neutral, because it results in a common feature being signalled via tags
* Bad, because it requires support for the feature to be verified on deployment of clients which use it

### Option 4a: Define an optional parameter in the core specification, with support signalled

This option would see the configuration of the feature be via a new parameter in the core spec.
This option would see support of this feature be optional.
This would see support for the feature signalled at the `/service` endpoint, similar to the signalling of support for event stream mechanisms.

* Good, because it avoids fragmented compatibility around a common function
* Neutral, because it requires a spec change
* Neutral, because it may tend towards a proliferation of features in the core spec
* Neutral, because it avoids a common feature being signalled via tags
* Bad, as the requirement to signal support for the feature would likely couple this feature to the Service Implementation

### Option 4b: Define an optional parameter in the core specification, with support not signalled

This option would see the configuration of the feature be via a new parameter in the core spec.
This option would see support of this feature be optional.
This would see no signalling of support for the feature via the API.
It would be up to integration engineers to ensure that the feature is provided by the Service Implementation, or some other mechanism, when they deploy a client that needs to use it.

* Good, because it avoids fragmented compatibility around a common function
* Neutral, because it requires a spec change
* Neutral, because it may tend towards a proliferation of features in the core spec
* Neutral, because it avoids a common feature being signalled via tags
* Bad, because it requires support for the feature to be verified on deployment of clients which use it

### Option 4c: Define an optional parameter in the core specification, with mandatory support

This option would see the configuration of the feature be via a new parameter in the core spec.
This option would see support for this feature be mandatory.

* Good, because it avoids fragmented compatibility around a common function
* Neutral, because it requires a spec change
* Neutral, because it may tend towards a proliferation of features in the core spec
* Neutral, because it avoids a common feature being signalled via tags
* Bad, because it requires Service Implementations to support a feature that will only be used by a relatively small subset of deployments

### Option 5a: Describe a method of deleting Segments after a period of time from their registration

This option would require additional Segment metadata.
We do not currently store the creation time for Segments.
Adding this metadata to every Segment would represent a significant increase in the amount of data stored in TAMS.
It may also result in unexpected behaviour where Segments are written out of order.
This type of behaviour could be more reliably implemented by Option 5c.

* Neutral, because it requires a spec change
* Bad, because it requires significantly more data to be stored by a TAMS service
* Bad, because it may have unexpected behaviour

### Option 5b: Describe a method of deleting Segments at a time offset from their TimeRange end

This option would see an offset specified that will be added to the TimeRange end of a segment to determine when it shall be deleted.
Alternatively, the offset could be subtracted from the current time to be provided as `_<calculated_time>)` in the `timerange` query parameter on DELETE requests to the Flow's segment delete endpoint.
This can be run at regular intervals with a single API request and no need to query the segments endpoint.

* Good, because it doesn't require a spec change
* Good, because it enables loop recorder implementations with minimal requests
* Neutral, because a Flow that is no longer being written to will tend towards all Segments being deleted

### Option 5c: Describe a method of deleting Segments to maintain a maximum duration for a Flow

This option would see a target duration specified.
The loop recorder system would get the TimeRange end of the latest segment via a GET request to the `/segments` endpoint with `limit` set to `1` and `reverse_order` set to `true`.
The loop recorder would then subtract the specified duration from end Timestamp of the returned Segment to calculate the end timestamp for the delete request.
This would then be provided as `_<calculated_time>)` in the `timerange` query parameter on DELETE requests to the Flow's segment delete endpoint.
The potentially unexpected behaviour of this option is that Flows with gaps may end up with much less content present than the duration specified would imply.

* Good, because it doesn't require a spec change
* Neutral, because it requires multiple requests per delete cycle
* Neutral, because a Flow that is no longer being written to will maintain a stock of Segments
* Bad, because behaviour may be unexpected on Flows with gaps

### Option 6a: Describe a method of deleting an entire Flow at a specific time

This option would see the time for a Flow's automated deletion to be signalled with an absolute time.

* Good, because it is immediately obvious when a Flow will be deleted
* Neutral, because enacting this requires no further calculations
* Bad, because this mode of operation cannot be statically templated

### Option 6b: Describe a method of deleting an entire Flow at a time offset from its `created` time

This option would see the time for a Flow's automated deletion to be signalled with an offset to be applied to the Flow's `created` time.

* Good, because it supports static templating (e.g. via Flow Profiles)
* Neutral, because enacting this requires a simple calculation to identify the actual time for deletion
* Neutral, because it allows Flows to be assigned an explicit life time
* Bad, because it doesn't take into account whether the Flow is still being written to

### Option 6c: Describe a method of deleting an entire Flow at a time offset from its `segments_updated` time

This option would see the time for a Flow's automated deletion to be signalled with an offset to be applied to the Flow's `segments_updated` time.

* Good, because it supports static templating (e.g. via Flow Profiles)
* Good, because it allows Flows to be assigned an explicit life time beyond when Segments are written to it
* Neutral, because enacting this requires a simple calculation to identify the actual time for deletion

### Option 6d: Describe a method of deleting an entire Flow at a time offset from the most recent of `segments_updated` or `metadata_updated` time

This option would see the time for a Flow's automated deletion to be signalled with an offset to be applied to the Flow's the later of `segments_updated` or `metadata_updated` time.

* Good, because it supports static templating (e.g. via Flow Profiles)
* Good, because it captures any type of Flow modification
* Neutral, because enacting this requires a simple calculation to identify the actual time for deletion
* Neutral, because it allows Flows to be assigned an explicit life time beyond when the Flow metadata was last modified

### Option 7: Describe potential implementation architectures in an Application Note

This option would be combined with any of the above signalling options.
It would see an Application Note produced describing possible approaches to implementing loop record functionality.

* Good, because it reduces the design work required on the part of implementers of such functionality
