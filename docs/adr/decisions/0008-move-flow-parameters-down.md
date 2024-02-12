---
status: "proposed"
---
# Move Flow Parameters into a sub-property

## Context and Problem Statement

Currently a Flow object is a flat list of both the properties common to all Flows (e.g. Flow and Source IDs, tags, type, created and modified fields) and also those specific to the type of Flow and the codec in use.
It would be easier to work with Flow objects if the type-specific metadata were in a sub-property.

## Decision Drivers

* The Flow schema is made more complex by the need for different properties based on the type
* While this would be a breaking change, at present it only affects the internal implementation.
  It would be more difficult to change in future.

## Considered Options

* Option 1: Change the schema to add a new property containing Flow type specific properties
* (Option 0: Reject the proposal, keep Flows as is)

## Decision Outcome

Chosen option: Option 1, because it makes the API easier to work with, and there is no hard requirement for alignment with the NMOS model.

### Consequences

* This is a breaking change to the API, and will trigger a major version increment
* Existing clients and store implementations will need rework to support the new version

### Implementation

<https://github.com/bbc/tams/pull/28>

## Pros and Cons of the Options

### Option 1: Change the schema to add a new property containign Flow type specific properties

Create a new key in the Flow object containing the technical metadata about that Flow, named specifically for each Flow type (`format`) supported.
For example a video Flow gains a `video` property containing the video-specific details (which is in turn amended to add more nesting where needed, e.g. for codec-specific options).

* Good, because it is easier for clients that aren't interested in technical Flow metadata to ignore it
* Good, because it makes clearer what properties are expected on each Flow format
* Good, because it makes it easier to add more media types or additional properties in future
* Bad, because it is a breaking change, although there are few known implementations of TAMS at the time of writing
