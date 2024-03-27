---
status: "proposed"
---
# Add collections to flow and source metadata schemas

## Context and Problem Statement

For optimum flexibility, media Flows (and their parent Sources) are defined as mono-essence.
However, for all practical purposes, a means of describing how separate mono-essence Flows relate together is needed.
As an example, media is often streamed as a multiplex of audio, video and ancillary essence such as subtitles.
These elements are intended to be presented together in sync.
When ingested into a TAM store, these media elements may be stored separately, with their synchronisation relationship communicated through timestamps placing them on a common timeline.
Each element has a separate Flow ID and descriptor.
A client of the API needs to be able to discover the fact that these elements were ingested as a group.
Beyond this, it would be useful to be able to define new collections or presentation groups built from elements that share a common timeline.
For example, commentary or subtitles may be added as new or replacement elements after the initial ingest of an AV feed.

## Considered Options

* Option 1: Delegate the handling of grouping relationships to a separate service with its own API
* Option 2: Add multi-essence Sources that register collections of Sources in the TAMS API
* Option 3: Add multi-essence Flows that register collections of Flows in the TAMS API
  * Option 3a: Reflect Source relationships inferred by Flow relationships described in Option 3 in the API

## Decision Outcome

Chosen option: Option 3/3a: Add multi-essence Flows that register collections of Flows in the TAMS API, because

1. This facility is needed for even the most basic use cases
2. The TAMS API needs to be self-contained for simple, minimal configurations
3. Adding collections at the Source level (option 2) doesn't provide all the information required to describe the corresponding relationships at the Flow level

Extending this to add Option 3a would be desirable, but could be added later (recommend implementing sooner if tracking Source <-> Source relationships is deemed a requirement, or this will have to be implemented by all clients that need it).
Proposed API implementation covers both option 3 and 3a.
Read-only Source attributes relating to collections are optional, and can be omitted by system implementers if not required initially.

### Consequences

* Good, because it provides a simple way to group media elements together into collections
* Bad, because traversing the hierarchy via the TAMS API is more inefficient and clunky than a dedicated relationships API might be

### Implementation

Implemented by <https://github.com/bbc/tams/pull/35>

## Pros and Cons of the Options

### Option 1: Delegate the handling of grouping relationships to a separate service with its own API

Another system and API could be specified and built that stores relationships.  
That system could be queried with a graph-based interface and a richer data model, cross-referenced with the Source and Flow entities registered through the TAMS API.

* Good, because a for-purpose solution can provide a more complete data model
* Good, because it can provide access to navigate the hierarchy and Source graph in an efficient way, building on graph database techniques
* Neutral, because it limits the scope and complexity in the TAMS API, at the expense of moving it to another system ("complexity never goes away, it only moves")
* Bad, because without that other system basic operations (such as finding video and audio that belong together) becomes impossible
* Bad, because it requires creating an entire additional API, model and reference implementation

### Option 2: Add multi-essence Sources that register collections of Sources in the TAMS API

Add a new optional attribute to the Source resource that collects together a list of mono-essence Sources into a multi-essence Source.  
Add a new (read-only) attribute to the Source resource that lists multi-essence Sources that reference this Source.

* Good, because it provides a way of collecting together mono-essence entities at the Source level
* Bad, because these relationships at the Source level don't provide all the information needed to infer the corresponding Flow <-> Flow relationships

### Option 3: Add multi-essence Flows that register collections of Flows in the TAMS API

Add a new optional attribute to the Flow resource that collects together a list of mono-essence Flows into a multi-essence Flow.  
Add a new (read-only) attribute to the Flow resource that lists multi-essence Flows that reference this Source.

* Good, because it provides a way of collecting together mono-essence entities at the Flow level
* Good, because the practical problem of recording grouping relationships between media elements is solved
* Neutral, because it doesn't directly provide the corresponding relationships at the Source level, although these can be inferred

### Option 3a: Reflect Source relationships inferred by Flow relationships described in Option 3 in the API

Add read-only attributes to Source resources that reflect the relationships with other Sources that can be inferred from Flow collection attributes.  
This would avoid clients having to figure this out for themselves from the Flow <-> Flow and the Source <-> Flow relationships.

* Good, because it reduces complexity for clients
* Neutral, because it increases complexity slightly for TAMS implementations (and it's one more thing to implement!)

<!-- This is an optional element. Feel free to remove. -->
## More Information

__Note:__ 0002-add-sources-to-api.md contains some discussion that may be relevant to this proposal

### Implementation note

Implementing this feature will likely require an underlying database to store the relationships, to provide a single source of truth from which relationships can be surfaced into the relevant Source and Flow attributes.
