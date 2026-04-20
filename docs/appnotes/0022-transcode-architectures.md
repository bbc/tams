# 0022: Architectures for the transcoding of media

## Abstract

A common use case in TAMS systems is to transcode or transpackage media to provide multiple formats, and qualities.
This application note discusses the available architectures that may be used when implementing this functionality, and discusses the pros and cons of each.

> [!NOTE]
> Where this application note refers to "transcode", the transpackage use case is equally applicable unless otherwise stated

## Basic Transcode on Ingest

In this architecture, transcode is the responsibility of the ingest client.
When media is written to TAMS, the ingest client is configured to transcode the media and write multiple Flows of the same Source to TAMS.
Ingest clients must take care that timing is aligned between all generated Flows of the Source.

### Pros

* Many ingest clients have added TAMS capability to existing products which already include this capability
* The ingest client may have access to a higher quality copy of media than the one(s) written to TAMS
* In many cases, this will be the most simple architecture

### Cons

* Transcode may take place even if likelihood of the transcoded media being used is low
* Transcode in the ingest client will result in higher ingress bandwidth use compared to transcode within the TAMS Service's compute environment

## Event-triggered Transcode on Ingest

In this architecture, a transcode service subscribes to the webhooks endpoint to receive events for new Segments.
The transcode service will fetch these Segments, transcode them based on the transcode services configuration, and write them to a new Flow.

### Pros

* Ensures appropriate formats are available for all media, where standard formats are required (e.g. proxies)
* Requires no action by ingesting or consuming clients
* Potentially allows for more complex configuration of transcoders
* Potentially allows for transcode service to be deployed in close (logical) proximity to the TAMS Service

### Cons

* Requires an additional component (the transcode service) in the deployment
* Transcode may take place even if likelihood of the transcoded media being used is low

## Manually-triggered Transcode

In this architecture, a transcode of an entire Flow is manually triggered by a client.
This may be done via a call to a 3rd-party API, or by creating a new Flow with the `trigger_transcode` tag set to `immediate`.

### 3rd-party API

In the case of the 3rd-party API approach, a client makes a request to the the transcode service with the Source ID of the media to be transcoded, optionally the timerange to be transcoded, and optionally the output format.
The transcode client will then register a new Flow of the same Source, and provide the Flow ID to the requesting client.

The transcode client will transcode each Segment in the originating Flow, and write the resultant media back to TAMS against the destination Flow.
The transcode client should set the destination Flow's `flow_status` tag to `awaiting_content` on initial registration, `ingesting` on first write of a Segment, and `closed_complete` once the transcode is complete.

Where the originating Flow has a `flow_status` of `ingesting`, the transcode client may need to subscribe to `flows/segments_added` webhook events for the originating Flow and transcode new Segments as they become available.

The transcode client may be designed such that all Segments are transcoded in parallel, allowing for faster than real-time transcodes in many cases.

#### Pros

* Keeps control signalling out of the TAMS API
* Potentially allows for more complex configuration of transcoders
* Potentially allows for transcode service to be deployed in close (logical) proximity to the TAMS Service

#### Cons

* Requesting clients must integrate with additional APIs
* More components may mean a more complicated architecture

### Tags

In the case of the Flow tag approach, the transcode service will subscribe to `flows/created` webhook events and identify those with the `trigger_transcode` tag set to `immediate`.

The requesting client will create a new Flow against the existing Source with the required codec and properties, and the `trigger_transcode` tag set to `immediate`.
The creation of this Flow will result in an event that will be received by the transcode service configured above.

The transcode service will transcode each Segment in the originating Flow, based on the technical properties of the destination Flow, and write the resultant media back to TAMS against the destination Flow.
The transcode service should set the destination Flow's `flow_status` tag to `awaiting_content` on initial registration, `ingesting` on first write of a Segment, and `closed_complete` once the transcode is complete.
When the transcode is complete, the `trigger_transcode` tag should be removed from the originating Flow.

Where the originating Flow has a `flow_status` of `ingesting`, the transcode service may need to subscribe to `flows/segments_added` webhook events for the originating Flow and transcode new Segments as they become available.

The transcode service may be designed such that all Segments are transcoded in parallel, allowing for faster than real-time transcodes in many cases.

#### Pros

* Requesting clients integrate with fewer APIs
* Potentially allows for transcode service to be deployed in close (logical) proximity to the TAMS Service

#### Cons

* Adds control signalling to the TAMS API
* Potentially impedes more complex configuration of transcoders
* More components may mean a more complicated architecture
