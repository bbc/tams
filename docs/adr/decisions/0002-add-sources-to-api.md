---
status: proposed
---
# Add Sources as objects in the API

## Context and Problem Statement

Most workflows and systems are interested in Sources: they want to think about an asset (or a version of an asset) and only look at the specific representation when it becomes relevant.
However the TAMS API entirely works in Flows, and only provides a basic list of Sources, making it harder to use.

_Note: The [NMOS Timing and Identity Model](https://specs.amwa.tv/ms-04/releases/v1.0.0/docs/2.1._Summary_and_Definitions.html) provides definitions of Source and Flow in this context, and may be useful background reading_

## Decision Drivers

* Systems need to bridge workflow assets (e.g. a recording, or a programme) with the relevant content in TAMS, which should be linked to the Source ID.
* Existing demos and uses of TAMS operate based on Flow IDs, which is at odds with how the model is supposed to work and leads to inflexibility.
* Sources naturally for a hierarchy (Flows do not), which should be used to traverse relationships between content.
* It is necessary to have some way to attach business metadata to Sources and then find them in order to build demos.
  While in principle this should be another system that stores the Source ID, in practice no such system will be built imminently.

## Considered Options

* Option 1: Add a lightweight Source representation to the TAMS API
* Option 2: Specify and build another system to store Source <-> Source relationships
* Option 3: Assume other systems will work exclusively in Flow IDs

## Decision Outcome

Chosen option: Option 1: Add a lightweight Source representation to the TAMS API.

This option balances the need to avoid overloading the API (by adding parts of a MAM into scope) with the need for something that works out-of-the-box.
It should be possible to approach the proposed API using Sources, and to traverse the Source hierarchy, however the latter will only be efficient enough for proof-of-concept: anything more advanced indicates the need for another system.

### Implementation

Implemented by <https://github.com/bbc/tams/pull/18>

## Pros and Cons of the Options

### Option 1: Add a Source representation

Add Sources as a more complete element to the API (and by extension, the database that backs it), with basic CRUD operations.
Sources can be created, have Flows attached to them, and a basic hierarchy can be assembled where Sources can be composed to produce muxed Sources.
Sources can also have tags, providing a very basic way to query them.

* Good, because any compliant TAMS implementation has some common understanding of Sources
* Good, because it is possible to navigate the Source hierarchy (albeit in a very limited way) to find Flows of interest
* Good, because a lot of use cases can be built to a proof-of-concept level by using Source tags to store business metadata and then query it later
* Neutral, because it adds additional complexity to the API and implementations, but that complexity has to go somewhere
* Bad, because Source data are potentially duplicated between this API and other systems (e.g. external MAM/PAM systems)

### Option 2: Specify and build another system to store Source <-> Source relationships

Another system and API could be specified and built that stores the Source <-> Source relationships.
That system could be queried with a graph-based interface and a richer data model, eventually resolving down to a single Source ID which is cross-referenced to the TAMS API to find Flows.

* Good, because a for-purpose solution can provide a more complete data model
* Good, because it can provide access to navigate the hierarchy and Source graph in an efficient way, building on graph database techniques
* Neutral, because it limits the scope and complexity in the TAMS API, at the expense of moving it to another system ("complexity never goes away, it only moves")
* Bad, because without that other system basic operations (such as finding video and audio that belong together) becomes impossible
* Bad, because it requires creating an entire additional API, model and reference implementation

### Option 3: Assume other systems will work exclusively in Flow IDs

Reduce the importance of Sources in the model by assuming that other systems and workflows will work exclusively in Flow IDs, and will maintain their own understanding of the relationships between those Flows.

* Good, because it requires no changes to the TAMS API
* Neutral, because it aligns with existing mental models of file-based working, but TAMS is intended to improve those models.
* Bad, because matching equivalent content (e.g. proxy edit workflows) becomes difficult or brittle
* Bad, because finding other content in the hierarchy (e.g. matching audio and video together) becomes impossible
* Bad, because it loses alignment with the NMOS model
