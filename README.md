# Time-addressable Media Store API

This repository contains API definitions for a Time-addressable Media Store (TAMS) server, which can be used to store, query and access segmented media - distinct from files and streams, but sharing characteristics of both.

BBC R&D have demonstrated use of the TAMS approach as part of composable, software-defined workflows which can run in the cloud, on-premise or in a hybrid environment.
We've built a prototype implementation of this API, along with services for movement and transformation of streams and files, which serve as the media backend for other projects such as our [remote wildlife camera](https://www.bbc.co.uk/rd/blog/2022-04-video-cloud-media-store-ingest-service) work.

Time-addressable media is defined by a timeline, with media elements placed upon it, building upon concepts familiar from IMF.
Media stored in TAMS are identified with UUIDs according to the scheme used in [AMWA NMOS IS-04](https://specs.amwa.tv/is-04/releases/v1.3.2/APIs/schemas/).
Once written, the media, and their association with the timeline, are immutable.

Thanks to this immutability, a UUID and a timerange always refers to a specific sequence of media.
Unless you need to read the samples, you don’t need to copy the media, instead just working by reference.
Metadata operations can all be carried out without moving media files around, so lightweight metadata operations can have lightweight implementations.

We designed TAMS cloud-first.
When run on public cloud services TAMS benefits from the scalability, robustness and availability of any well-designed cloud service.
Freed from the limitations of a fixed-size appliance, the TAMS can become the core of a whole media ecosystem.
Next-generation tools and systems communicate via, or with reference to, the store, just by making HTTP requests.
Immutability means that references are always valid.
Wide availability means large organisations like the BBC can easily share assets between staff and partners.
Access controls can be put in place as needed for business reasons, using standard web security techniques, rather than being imposed by technical limitations.

Thanks to adopting cloud-style separation of concerns, essence storage is delegated to a cloud service.
As a result storage can be chosen on a flexible and dynamic basis.
Media can be moved between locations and storage tiers as needed.
Users of TAMS are insulated from the details of the underlying storage.

## Documentation

- OpenAPI Specification: [TimeAddressableMediaStore.yaml](./api/TimeAddressableMediaStore.yaml)
- Rendered Documentation: [https://bbc.github.io/tams](https://bbc.github.io/tams)
- Supporting Documentation: [docs/README.md](./docs/README.md)
- Example API Usage Scripts: [examples/README](./examples/README.md)

This repo contains some automation to run a mock version of the API using [Stoplight Prism](https://stoplight.io/open-source/prism).
To run the mock server using Docker, try something like the command below (or run `make mock-server-up`):

```shell
docker run --rm --init --name mock-tams -v "$(pwd)":/data:ro -p 4010:4010 stoplight/prism mock /data/TimeAddressableMediaStore.yaml -h 0.0.0.0
```

A mock API server will start at <http://localhost:4010>

## Design

The store handles Flows which exist on an infinite timeline, are immutable, and can be grouped by Sources (based on the Flows and Sources in the [AMWA NMOS MS-04 model](https://specs.amwa.tv/ms-04/releases/v1.0.0/docs/2.1._Summary_and_Definitions.html)).
A flow ID and timerange refers to a sequence of grains (_e.g._ frames of video or set of audio samples) and any point in a Flow can be uniquely addressed by a `<flow_id, timestamp>` tuple.
This unique address is guaranteed to refer to a specific frame, or set of audio samples, so it can be safely passed around other tools or programs.
At any time the unique address can be exchanged for the media data by an API call.
But if that is not needed, media work can be done purely by reference.

Grains are grouped into Flow Segments, containing for example one second of content, wrapped in a container format such as MPEG-TS.
The store provides a mechanism to upload and register new Flow Segments, and an interface to request all the Flow Segments covering a particular timerange and their download URLs; an approach inspired by chunked streaming protocols like HTTP Live Streaming.

The media data contained within Flow Segments may be stored separately from the metadata linking them to a position on the timeline, separating the media data and metadata planes.
For example our implementation uses a database (_e.g._ Amazon DynamoDB) to store Flow Segment metadata and an object store (_e.g._ AWS S3) to store the media data for Flow Segments.
We refer to media data stored in the object store as 'media objects'.
The Flow Segment has a list of S3 download urls which are the location of the media object(s) that contains the stored media data for the Flow Segment.
If multiple URLs are returned in the list, they are assumed to return identical media data.
When writing to the store, the S3 URLs can be passed to a client permitting them to upload media data directly.

Another advantage of separating the media data and metadata planes in this way is that a particular Flow Segment can be referenced by multiple flows.
On the metadata side, the Flow Segment is just an object ID, so any number of flows can record that same ID against other `<flow_id, timestamp>` tuples.
This allows for copy-on-write semantics: immutability means a new Flow must be created to make changes to existing parts of the timeline, but for unmodified portions of the timeline the new `<flow_id, timestamp>` tuple points to the existing object ID or a part of it.
See [Flow And Media Timelines](#flow-and-media-timelines) for a description of how that works in practice.

The Flow model is aligned with the principles and schemas of [AMWA NMOS IS-04](https://specs.amwa.tv/is-04/releases/v1.3.2/APIs/schemas/) to facilitate easy integration of NMOS-compliant media devices.

### Reading and Writing in the Store

The process of reading from the store is:

1. Client identifies the Flow ID and timerange of interest
2. Client makes a request to [`GET flows/<flow_id>/segments?timerange=<timerange>`](https://bbc.github.io/tams/5.1/index.html#/operations/GET_flows-flowId-segments) and receives a list of Flow Segments, including their timeranges and download URLs
3. Client downloads each URL, concatenates the Flow Segments together and unwraps the grains within
4. The first and last Flow Segment may contain more grains than requested, so the client should skip any received not in the requested timerange

The process of writing to the store is:

1. Client creates a Flow if necessary by making a request to [`PUT flows/<flow_id>`](https://bbc.github.io/tams/5.1/index.html#/operations/PUT_flows-flowId)
2. Client makes a request to [`POST flows/<flow_id>/storage`](https://bbc.github.io/tams/5.1/index.html#/operations/POST_flows-flowId-storage) and receives a list of URLs to PUT media data into, along with an optional `pre` URL to call before writing
3. If a `pre` URL was given, client calls it
4. Client breaks content into Flow Segments (each of which should contain complete decodable units, _e.g._ a number of complete GOPs for video) and uploads the corresponding media data
5. Client makes requests to [`POST flows/<flow_id>/segments`](https://bbc.github.io/tams/5.1/index.html#/operations/POST_flows-flowId-segments) with details of each new Flow Segment created, to register them on the timeline

### Sources

Sources represent the abstract concept of a piece of content, which can be represented by a (or a number of) Flows, as described in <https://specs.amwa.tv/ms-04/releases/v1.0.0/docs/2.1._Summary_and_Definitions.html>.
For example a video Source might be represented by a Flow for the original content, and another Flow containing a lower-bitrate proxy.
Sources can also be collected into other Sources - for example a video Source and an audio Source contribute to another Source representing the muxed content.
Conventionally the store contains elemental Flows, represented by elemental Sources, which are collected into muxed Sources, although the model also makes it possible to represent a muxed Source with a Flow (e.g. representing a muxed file).

Media workflows and applications are likely to use Sources as their references to media, for example a MAM might reference an asset using the ID of a muxed Source (in lieu of a filename).
Then some logic can be applied to identify a suitable Flow representing that Source at the point when operations need to be performed on the media, for example choosing between proxy-quality for an offline edit and full-quality for a render.

The TAMS API stores both Flows and Sources, each of which can be assigned a label, description and some tags alongside relevant technical metadata.
Flows can be collected into other Flows (with a `role` parameter to ascribe meaning to the relationship).
Sources can collect together other Sources, by inference from the relationships defined by their Flows.
This implementation is deliberately kept very simple, and lacks efficient mechansisms to query the graph of Sources and Flows.
More sophisticated mechanisms for recording and querying relationships between model entities is out of scope for this API, but could in principle be provided by a separate complementary service dedicated to that purpose in the future.

### Mutation

Flows in the store are assumed to be immutable: once a grain has been written to a point on the timeline on a specific Flow, it cannot be changed.
However Flows can always be extended, with empty spaces on the timeline filled in, and areas of the timeline can be permanently erased.

When it becomes necessary to mutate content, for example reversioning content or performing production operations, the Flow ID (and potentially Source ID) will change.
Various scenarios are explored in the [Practical Guidance for Media](https://specs.amwa.tv/ms-04/releases/v1.0.0/docs/3.0._Practical_Guidance_for_Media.html) section of AMWA MS-04.

### Flow and Media Timelines

Flows exist on an infinite timeline (the "Flow timeline"), and the position of content on this timeline is defined by the `timerange` attribute in each Flow Segment of that Flow.
A timerange is represented in JSON and text using the [TimeRange string pattern](https://bbc.github.io/tams/5.1/index.html#/schemas/timerange).
Separately the media objects have a timeline (the "media timeline") defined by the container format itself: the timestamps recorded inside the media object for each grain.
The Flow Segment attributes describe how to map the media timeline onto the Flow timeline.
For Flows using codecs with temporal re-ordering, both of these timelines represent the presentation timeline of the media.
Note that no explicit relationship is defined between the Flow timelines of different Flows, although a mechanism to define that may be added in future.

For brevity these diagrams start at `0:0`, however it is likely a practical system would stick closer to wall-clock time or TAI, such as starting at `1709634568:0`.
A timestamp is represented in JSON and text using the [Timestamp string pattern](https://bbc.github.io/tams/5.1/index.html#/schemas/timestamp).

![Graphic showing the Flow timeline and 3 Flow Segments in Flow A, with a media timeline showing 10 samples in each object](./docs/images/Flow%20and%20Media%20Timelines-Flow%20A.drawio.png)

In the case of Flow A in the diagram above, this is a 1:1 mapping.
However, in the diagram below the media timeline and Flow timeline differ, because the objects in Flow B have been re-used from Flow A (note the use of the same object ID).
These re-used objects have their original media timeline, and each grain's position on the Flow timeline can be calculated as `media_timeline + ts_offset`.

![Graphic showing the Flow timeline and 2 Flow Segments in Flow B, where the objects have been re-used from Flow A and the ts_offset set to -1:0](./docs/images/Flow%20and%20Media%20Timelines-Flow%20B.drawio.png)

Flow Segments can also re-use parts of a media object, as in Flow C in the diagram below.
Notice that the `timerange` still refers to the Flow timeline (and `0:50...` etc. is used as shorthand for `0:500000000`), however a reduced number of grains have been selected, taking only part of the first object and part of the last object.

![Graphic showing the Flow timeline and 3 Flow Segments in Flow C, where the objects have been re-used from Flow A however only half of the first and last object has been used](./docs/images/Flow%20and%20Media%20Timelines-Flow%20C.drawio.png)

In this way a simple copy-on-write mechanic can be applied to the store, for example when taking "clips" from multiple Flows and assembling them, the original media objects (and therefore essence) can be referenced, and new media objects are only required to handle changes, for example transitions.
In the diagram below, portions of Flow X and Flow Y are combined to form Flow Z, along with some rendered transitions which are "new" media, and new objects accordingly.

![Graphic showing the Flow timeline and Flow Segments of Flows X, Y and Z, where Z is composed of a mix of re-used segments and new media](./docs/images/Flow%20and%20Media%20Timelines-Flow%20XYZ.drawio.png)

### Events from the API

The TAMS API specifies a list of event messages that should be generated and sent to interested clients in response to certain events, such as the creation of a new Flow.
This is intended to reduce the amount of polling required by clients to keep up with activity on a store by providing a way to push updates about content they have access to instead.

However the specification is deliberately left open-ended; only the message bodies are specified, but not the protocol by which they are carried nor the method by which clients subscribe.
It is assumed that implementations will provide a suitable mechanism, such as a call to allow clients to subscribe to webhooks, or details of an event bus to connect to and receive the messages.

### API Versioning

The API is versioned using a major and minor version number.
A breaking change - such as removal of a feature, or renaming of properties in such a way that would break compatibility (including fixing a typo) - results in a major version increment and the minor version is reset to 0.
Features such new endpoints or new (optional) data properties result in a minor version increment.
Other changes such as documentation changes do not result in version updates.
Note that the version may change frequently whilst the API is still under development!

Versions are calculated automatically upon release using 'magic' strings included in commit messages:
    - `sem-ver: api-break` - where a breaking change is made (results in a major version bump)
    - `sem-ver: feature` - where a new feature has been added (results in a minor version bump)
    - `sem-ver: deprecation` - where an existing feature has been marked as deprecated, but not yet removed (results in a minor version bump)
Commits without one of these magic strings are assumed to be unsubstantial and will not result in a version bump.
Versions will only be incremented once when a release is made.
If there are multiple commits since the last release, the major version number will be incremented by 1, and minor version set to 0 if at least one of the commits contains an `api-break`.
If there are no `api-break` changes since the last release, the minor version will be incremented by 1 if at least one commit contains a `feature` or `deprecation` change.
Otherwise, the version will not change.

It is possible to see what the version would be if a release was made at the current commit by running `make next-version` in the top directory of this repository.

### Security

The TAMS specification stipulates authentication methods that a client should support in order to identify themselves and provide credentials to the server, using standard HTTP approaches.
The authorisation model (the rules by which authenticated requests are allowed or denied) is not part of the TAMS specification, and is up to individual implementers and organisations depending on their exact rules, needs and threat model.
However some principles and suggestions are discussed in [AppNote0016: Authorisation in TAMS workflows](./docs/appnotes/0016-authorisation-in-tams-workflows.md).

It is assumed that implementations will apply other IT and cloud infrastructure security best practices, notably including the use of TLS (e.g. HTTPS connections) within and between their systems.

## Proposals, Decisions and Architecture Changes

This repository uses [(M)ADR documents](https://adr.github.io/madr/) to propose significant changes, facilitate discussions and decision making, and to store a record of options that were considered.
These documents may be found in the [docs/adr](./docs/adr/) directory, and are managed as described by the [ADR Readme](./docs/adr/README.md).

## Making a release

Run the `release` workflow under the `Actions` tab on this repository on GitHub against the `main` branch.
This workflow requires approval.
This workflow will fail if it does not identify any commits that would result in a version bump (see [API Versioning](#api-versioning)).

## Get in touch

If you'd like to know more about our work on TAMS, talk about our implementations or start a collaboration, contact us on <cloudfit-opensource@rd.bbc.co.uk>.
Also see [CONTRIBUTING.md](./CONTRIBUTING.md) for more about how to make contributions.
