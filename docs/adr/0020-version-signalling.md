---
status: "accepted"
---
# Improving the signalling of the supported API version in implementations

## Context and Problem Statement

The version of TAMS implemented by a service is currently signalled via the `version` property returned by the `/service` endpoint.
This property is vaguely defined and combines both the TAMS API version and the software version of the deployed service.

## Decision Drivers

* The lack of concrete definition of the format of the `version` string prevents implementations of clients from checking compatibility with a given service
* The combining of the TAMS API version and software version means the string in `version` must be processed by the client to extract the API version before determining compatibility
* The inclusion of the version of the deployed service may present a security risk in that it makes identifying deployments of known vulnerable software versions trivial

## Considered Options

* Option 1: Define the formatting of the string contained in `version`
* Option 2: Split out the TAMS Version and software version, making both required in the returned data of `/service`
* Option 3: As 2, but only the TAMS version is required

## Decision Outcome

Chosen option: "Option 3", because it makes use of the parametarised nature of JSON to explicitly signal each of the components of the current `version` string.
It makes the inclusion of the software version explicitely optional.
It removes the overhead on the client of processing the `version` string to extract the comoponents.

### Consequences

* Good, because it meets the requirements set in the Devision Drivers section
* Bad, because it is a breaking change
* Neutral, because it is a breaking change in a part of the API which isn't currently frequently used

### Implementation

Implemented in [https://github.com/bbc/tams/pull/62](https://github.com/bbc/tams/pull/62)
