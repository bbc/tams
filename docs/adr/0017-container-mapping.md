---
status: "accepted"
---
# Defining the Container Mapping to a Flow

## Context and Problem Statement

The addition of multi-essence Flows has meant that the mapping of the container essence data to the Flow may not be fully defined based on just the existing Flow metadata.

A container with a single track doesn't require additional metadata.
A container with tracks with different codecs also doesn't require additional metadata.
The container with multiple tracks with essentially the same Flow metadata does require additional metadata.

There may also be a need to define components of the essence data that are used in the Flow.
E.g. the set of audio channels.

## Considered Options

* Option 1: No container mapping
* Option 2a: Generic container track index mapping
* Option 2b: Generic container track index mapping for a format
* Option 3: Mapping that is specific to the container type
* Option 4: Mapping components of the track

## Decision Outcome

Chosen option: A combination of Option 2a, 2b, 3 and 4

There are cases, such as multi-essence containers, where there isn't a clear one-to-one mapping between a container track and the Flow.
This means option 1 is not viable.

Option 2a and 2b are useful if a track index is sufficient to ensure a one-to-one mapping without requiring container readers to have detailed knowledge of the internals of the container.
Option 3 allows for a potentially more accurate mapping that is specific to the container type.

The expectation is that mapping metadata is only provided if it is required to avoid a mapping error.
A combination of option 2a, 2b and 3 can be provided to cater for different container reader capabilities.
A container reader should try use metadata in order from option 3, 2b and 2a.

Option 4 allows selection of components within the track essence data, e.g. audio channels.
This option may be restricted to avoid complicating container reader implementations, e.g. limit it to uncompressed audio and require encoded audio to be re-encoded and stored separately if a selection of channels are used.

### Implementation

Implemented in PR [#46](https://github.com/bbc/tams/pull/46).

## Pros and Cons of the Options

### Option 1: No container mapping

The Flow metadata is assumed to be sufficient to determine which track in the container provides the essence data for the Flow.

* Good, because is requires no changes and works for mono-essence or video+audio containers
* Bad, because more complex multi-essence containers may not have a one-to-one mapping to the Flow

### Option 2a: Generic container track index mapping

The container is viewed as an ordered sequence of tracks.
The index in that sequence is used to identify the track

* Good, because it identifies tracks in all container types in the same way
* Bad, because it requires container readers to detect all tracks
* Bad, because it assumes container readers will apply the same track ordering

### Option 2b: Generic container track index mapping for a format

The container is treated as consisting of audio, video and data, where tracks for each format follow an ordered sequence.
The index in that sequence for the Flow format is used to identify the track

* Good, because it identifies tracks in all container types in the same way
* Good, because it avoids to some extent that container readers have to detect all tracks.
A container reader only need to detect all tracks for the Flow format
* Bad, because it requires container readers to detect all tracks for the Flow format
* Bad, because it assumes container readers will apply the same track ordering

### Option 3: Mapping that is specific to the container type

Each container type has a specific way to identify the tracks and this could be used map the track to the Flow.
E.g. MPEG-TS has a PID, MP4 a track ID and MXF a package and track ID.

* Good, because it uniquely identifies the container tracks
* Neutral, because it requires container readers and writers to have the information provided to them.
The software library that is used to read or write the container may not provide this information.

### Option 4: Mapping components of the track

The Flow may use only a component of the essence data of a container track.
E.g. an audio Flow may use some of the channels and possibly in a different order.

* Good, because it allows a Flow to use only a component of the essence data
* Bad, because it requires additional functionality in container readers to extract the components, which may require a decode and encode
