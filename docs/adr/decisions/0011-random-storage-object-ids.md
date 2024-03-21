---
status: "proposed"
---
# Random Storage Object IDs

## Context and Problem Statement

The TAMS `/storage` endpoint provides object IDs and URLs to PUT media objects to the object store.
The object IDs and URLs are arranged according to the Flow's storage segmentation rate, such that each storage segment (with object ID and URL) is assigned a timerange.
A client is required to store a media object such that the earliest media timestamp falls within the storage segment's timerange.

Should the TAMS store prescribe how the media is segmented by applications?

## Considered Options

* Option 1: Use the current segmentation strategy
* Option 2a: Each request returns new object IDs
* Option 2b: Each request only returns storage segments with media unavailable
* Option 3: Each request returns new object IDs and doesn't prescribed storage segments
* Option 4: TAMS provides segmentation hints

## Decision Outcome

Chosen option: Option 3: Return random object IDs and don't prescribed storage segments

It is unclear what hints could be provided to clients that would practically be usefull, and for that reason option 4 is not chosen.

### Implementation

Implemented in [#34](https://github.com/bbc/tams/pull/34).

## Pros and Cons of the Options

### Option 1: Use the current segmentation strategy

The TAMS assigns storage segments using the Flow's storage segmentation rate.
A storage segment covers a timerange, is assigned a media object ID and provides PUT URL for clients to use.
A client is required to store a media object such that the earliest media timestamp falls within the storage segment's timerange.
the timerange.

* Good, because the logic for segmenting media is simple to follow
* Good, because the media object is overwritten if writing again to a storage segment timerange
* Bad, because only a single media object can be written for each storage segment timerange
* Bad, because media is not always be ideally segmented at a fixed rate, e.g. variable size GOPs
* Bad, because the clients and applications are likely better placed to decide on segment lengths to balance throughput and latency

### Option 2a: Each request returns new object IDs

This option modifies option 1 to provide unique object IDs for each request to the storage endpoint.
This allows gaps to be filled because the object IDs change with each request and existing media objects that start in the storage segment timerange are not overwritten.

* Good, because gaps can be filled
* Good, because only storage segments with no or mising media is returns
* Bad, because media is not always be ideally segmented at a fixed rate, e.g. variable size GOPs
* Bad, because the clients and applications are likely better placed to decide on segment lengths to balance throughput and latency

### Option 2b: Each request only returns storage segments with media unavailable

This option extends option 2a to only return storage segments that has media unavailable.

* Good, because clients are only presented with storage segments that have no or missing media
* Good, because clients don't accidentally overlap / duplicate media in storage segments
* Bad, because TAMS needs to check (e.g. query a database) media availability
* Bad, because media is not always be ideally segmented at a fixed rate, e.g. variable size GOPs
* Bad, because the clients and applications are likely better placed to decide on segment lengths to balance throughput and latency

### Option 3: Each request returns new object IDs and doesn't prescribed storage segments

This option removes the segmentation layout and essentially just provides a list of unique object IDs and PUT URLs on each request to the storage endpoint.

* Good, because media can be segmented according to the properties of the media, e.g. segments containing complete GOPs
* Good, because clients and applications can decide on a segmentation strategy that fits their requirements for throughput and latency
* Neutral, because clients need to implement their own segmentation logic
* Neutral, because clients could accidentally overlap / duplicate media in storage segments if they don't check availability first
* Bad, because clients and applications may segment in a way that results in poor throughput and latency performance for a given TAMS store

### Option 4: TAMS provides segmentation hints

This option extends option 3 to provide hints to the client on how to segment to optimise throughput and latency performance.
These hints would be in the form of metadata provided by the TAMS API.

* Good, because clients and applications are guided to avoid poor throughput and latency performance for a given TAMS store
* Bad, because it is unclear what hints should be provided and how practically useful they would be to dynamically alter how clients segment media
