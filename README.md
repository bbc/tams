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
The store provides a mechanism to upload and register new segments, and an interface to request all the segments covering a particular timerange and their download URLs; an approach inspired by chunked streaming protocols like HTTP Live Streaming.

Segments may be stored separately from the metadata linking them to a position on the timeline, separating the metadata and data planes.
For example our implementation uses an object store (_e.g._ AWS S3) for the segments, passing S3 URLs to the client to upload directly and taking advantage of the scalability of cloud object storage.
Segments are also de-coupled from their point in the timeline by a link between their `<flow_id, timestamp>` tuple and the underlying object ID, so a single segment can appear at multiple points in multiple flows.
This allows for copy-on-write semantics: immutability means a new Flow must be created to make changes to existing parts of the timeline, but for unmodified portions of the timeline the new `<flow_id, timestamp>` tuple points to the existing object ID.

The Flow model is aligned with the principles and schemas of [AMWA NMOS IS-04](https://specs.amwa.tv/is-04/releases/v1.3.2/APIs/schemas/) to facilitate easy integration of NMOS-compliant media devices.

### Reading and Writing in the Store

The process of reading from the store is:

1. Client identifies the Flow ID and timerange of interest
2. Client makes a request to [`GET flows/<flow_id>/segments?timerange=<timerange>`](https://bbc.github.io/tams/#/operations/GET_flows-flowId-segments) and receives a list of segments, timeranges and download URLs
3. Client downloads each URL, concatenates the segments together and unwraps the grains within
4. The first and last Flow Segment may contain more grains than requested, so the client should skip any received not in the requested timerange

The process of writing to the store is:

1. Client creates a Flow if necessary by making a request to [`PUT flows/<flow_id>`](https://bbc.github.io/tams/#/operations/PUT_flows-flowId)
2. Client makes a request to [`POST flows/<flow_id>/storage`](https://bbc.github.io/tams/#/operations/POST_flows-flowId-storage) with the timerange to be written
3. Store responds with a list of segment timeranges and URLs to PUT segments to, along with an optional `pre` URL to call before writing
4. If a `pre` URL was given, client calls it
5. Client breaks content into segments as instructed and uploads it
6. Client makes requests to [`POST flows/<flow_id>/segments`](https://bbc.github.io/tams/#/operations/POST_flows-flowId-segments) with details of each new segment created, to register them on the timeline

### Flows, Sources and Mutation

Flows in the store are assumed to be immutable: once a grain has been written to a point on the timeline on a specific Flow, it cannot be changed.
However Flows can always be extended, with empty spaces on the timeline filled in, and areas of the timeline can be permanently erased.

When it becomes necessary to mutate content, for example reversioning content or performing production operations, the Flow ID (and potentially Source ID) will change.
Various scenarios are explored in the [Practical Guidance for Media](https://specs.amwa.tv/ms-04/releases/v1.0.0/docs/3.0._Practical_Guidance_for_Media.html) section of AMWA MS-04.

### API Versioning

The API is versioned using a major and minor version number.
A breaking change results in a major version increment and the minor version is reset to 0.
Features such new endpoints or new (optional) data properties result in a minor version increment.
Other changes such as bug fixes and documentation changes do not result in version updates.
Note that the version may change frequently whilst the API is still under development!

## Proposals, Decisions and Architecture Changes

This repository uses [(M)ADR documents](https://adr.github.io/madr/) to propose significant changes, facilitate discussions and decision making, and to store a record of options that were considered.
These documents may be found in the [docs/adr/decisions](./docs/adr/decisions/) directory, and are managed as described by the [ADR Readme](./docs/adr/decisions/README.md).

## Get in touch

If you'd like to know more about our work on TAMS, talk about our implementations or start a collaboration, contact us on <cloudfit-opensource@rd.bbc.co.uk>.
Also see [CONTRIBUTING.md](./CONTRIBUTING.md) for more about how to make contributions.
