# 0022: Architectures for the transcoding of media

## Abstract

A common use case in TAMS systems is to transcode or transpackage media to provide multiple formats, and qualities.
This application note discusses the available architectures that may be used when implementing this functionality, and discusses the pros and cons of each.

> [!NOTE]
> Where this application note refers to "transcode", the transpackage use case is equally applicable unless otherwise stated

## Basic Transcode on Ingest

In this architecture, transcode is the responsibility of the ingest client.
When media is written to TAMS, the ingest client is configured to transcode the media and write multiple Flows of the same Source to TAMS.

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

## Transcode on Request

This architecture sees transcode of media being triggered just-in-time when a consuming client attempts to read media segments in a format not currently available on-disk.

> [!NOTE]
> This option likely requires deep integration into the TAMS Service due to the potential creation and removal of Media Object Instances.

The requesting client will create a new Flow against the existing Source with the required codec and properties, and the `trigger_transcode` tag set to `virtual`.
The TAMS Service will populate Segments and Objects correlating with the timeline range covered by the original Segments.
These Objects will have instances that are "virtual".
That is to say that the Objects do not exist on disk.
When a GET request is performed with the instance URL, the Service will perform the transcode to create the segment and return it, as if the media existed on disk.

Where the originating Flow has a `flow_status` of `ingesting`, new virtual Segments should be created as new originating Segments are registered.

### Pros

* Transcode only takes place when a client attempts to use the transcoded media
* Requesting clients integrate with fewer APIs
* Transcode capability to be deployed in close (logical) proximity to the rest of the TAMS Service, due to its deep integration with it
* Fewer components potentially means a less complicated architecture overall

### Cons

* Adds control signalling to the TAMS API
* Potentially impedes more complex configuration of transcoders
* Deep integration adds more complexity to TAMS Service implementations
* Segments need to be short enough and transcode fast enough to respond to Object GET in a timely manner

### Extension - Segment Duration

While basic implementations may wish to maintain the Segment duration of the originating Flow, a more extensive implementation may allow output Segment duration to be configured.
This may be configured by setting the `segment_duration` in the new Flow's metadata.
The Service should carry out due diligence that the requested Segment duration is valid against restrictions such as possible GOP lengths.

This approach could, for example, allow media to go from single frame per Segment, to long-GOP, and vice-versa.
This capability may be particularly effective in the transpackaging use case, where different size segments may be generated with minimal overheads.

### Extension - Store Write-Back

Once created, the transcoded instance may be stored on an appropriate Storage Backend, registered against the Object, and the virtual instance removed from the Object.
This would enable the number of transcode processes to be minimised where instances may be re-used.
Implementers should consider the relative resource/cost use of storing to disk Vs re-transcoding.

### Extension - Pre-emptive Transcode

Implementations may wish to pre-empt future requests.
When Segments in Flow containing virtual Segments are requested, the implementation may transcode virtual Segments in close temporal proximity to the requested Segments.
How far and in which direction implementations pre-emptively transcode will depend on expected usage patterns and the speed of the transcode.
