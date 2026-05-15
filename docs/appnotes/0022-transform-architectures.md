# 0022: Architectures for the transforming of media

## Abstract

A common use case in TAMS systems is to transform media to provide multiple formats, qualities, or modify media in some way.
This application note discusses the available architectures that may be used when implementing this functionality, and discusses the pros and cons of each.

> [!IMPORTANT]
> This application note is primarily targeted at transcode, and transpackage operations.
> The architectures described in this application note may be applied to other transformations, but they may have additional considerations not described here.
> One important consideration is that if the media changes editorially (e.g. through a colour correction process) then the resultant media is considered a new Source and should be registered in the TAMS Service as such.

## Basic Transform on Ingest

In this architecture, transform is the responsibility of the ingest client.
When media is written to TAMS, the ingest client is configured to transform the media and write multiple Flows to TAMS.
Ingest clients must take care that timing is aligned between all generated Flows of the same Source.

### Pros

* Many ingest clients have added TAMS capability to existing products which already include this capability
* The ingest client may have access to a higher quality copy of media than the one(s) written to TAMS
* In many cases, this will be the most simple architecture
* A low bitrate proxy Flow may be uploaded prior to a higher bitrate Flow in low bandwidth environments where latency is of high importance

### Cons

* Transform may take place even if likelihood of the transformed media being used is low
* Transform in the ingest client will result in higher ingress bandwidth use compared to transform within the TAMS Service's compute environment
* Requires additional resources/capabilities on the ingest client

## Event-triggered Transform on Ingest

In this architecture, a transform service subscribes to the webhooks endpoint to receive events for new Segments.
The transform service will fetch these Segments, transform them based on the transform services configuration, and write them to a new Flow.

### Pros

* Ensures appropriate formats are available for all media, where standard formats are required (e.g. proxies)
* Requires no action by ingesting or consuming clients
* Potentially allows for more complex configuration of transformers
* Potentially allows for transform service to be deployed in close (logical) proximity to the TAMS Service

### Cons

* Requires an additional component (the transform service) in the deployment
* Transform may take place even if likelihood of the transformed media being used is low

## Manually-triggered Transform

In this architecture, a transform of an entire Flow is manually triggered by a client.
This may be done via a call to a 3rd-party API or, for transcode/transpackage, by creating a new Flow with the `trigger_transcode` tag set to `immediate`.

### 3rd-party API

In the case of the 3rd-party API approach, a client makes a request to the the transform service with the Source ID of the media to be transformed, optionally the timerange to be transformed, and optionally the transform configuration.
The transform client will then register a new Flow, and provide the Flow ID to the requesting client.

The transform client will transform each Segment in the originating Flow, and write the resultant media back to TAMS against the destination Flow.
The transform client should set the destination Flow's `flow_status` tag to `awaiting_content` on initial registration, `ingesting` on first write of a Segment, and `closed_complete` once the transform is complete.

Where the originating Flow has a `flow_status` of `ingesting`, the transform client may need to subscribe to `flows/segments_added` webhook events for the originating Flow and transform new Segments as they become available.

The transform client may be designed such that all Segments are transformed in parallel, allowing for faster than real-time transforms in many cases.

#### Pros

* Keeps control signalling out of the TAMS API
* Potentially allows for more complex configuration of transformers
* Potentially allows for transform service to be deployed in close (logical) proximity to the TAMS Service
* Where transform timerange is supported, enables a fine-grained approach to transform

#### Cons

* Requesting clients must integrate with additional APIs
* More components may mean a more complicated architecture

### Tags

> [!NOTE]
> This approach is only capable of signalling transformations that may be represented in Flow metadata.
> Practically, this means transcode and transpackage operations.
> As such, this section only refers to transcode and transpackage operations, rather than broader transformations.

In the case of the Flow tag approach, the transcode (or transpackage) service will subscribe to `flows/created` webhook events and identify those with the `trigger_transcode` tag set to `immediate`.

The requesting client will create a new Flow against the existing Source with the required codec and properties, and the `trigger_transcode` tag set to `immediate`.
The creation of this Flow will result in an event that will be received by the transcode service configured above.

The transcode service will transcode each Segment in the originating Flow, based on the technical properties of the destination Flow, and write the resultant media back to TAMS against the destination Flow.
The transcode service should set the destination Flow's `flow_status` tag to `awaiting_content` on initial registration, `ingesting` on first write of a Segment, and `closed_complete` once the transcode is complete.
When the transcode is complete, the `trigger_transcode` tag should be removed from the originating Flow.

Where the originating Flow has a `flow_status` of `ingesting`, the transcode service may need to subscribe to `flows/segments_added` webhook events for the originating Flow and transcode new Segments as they become available.

The transcode service may be designed such that all Segments are transcoded in parallel, allowing for faster than real-time transcodes in many cases.

Where the transcode service is deeply integrated with the API Service, creation of Flows with the `trigger_transcode` tag set to `immediate` but incompatible technical parameters may result in a `501` Not Implemented error.
The body of the response may include further details on the nature of the error.

#### Pros

* Requesting clients integrate with fewer APIs
* Potentially allows for transcode service to be deployed in close (logical) proximity to the TAMS Service

#### Cons

* Adds control signalling to the TAMS API
* Potentially impedes more complex configuration of transcoders
* More components may mean a more complicated architecture
* There are no obvious ways to communicate errors in-band where the transcode service is not deeply integrated that don't have significant drawbacks
