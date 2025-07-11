---
status: "proposed"
---
# Fine-grained Authorisation in TAMS Workflows

## Context and Problem Statement

TAMS provides multiple methods for authentication, as described in [ADR0028](./0028-authentication-methods.md).
The most commonly used method to implement authentication is Bearer tokens acquired using OAuth2 flows.
OAuth2 allows for auth tokens to claim [scopes](https://oauth.net/2/scope/) as a means to restrict the permissions of clients and requests.
This has been used in TAMS implementations to provide coarse grained authorisation.

Emerging TAMS use cases are making use of TAMS' media re-use capabilities over increasingly large numbers of users, teams, and organisations.
As the number of clients accessing content in a TAMS store grows, the need for finer-grained control of that content becomes more acute.

This ADR presents the decisions and considerations that informed the initial approach to fine-grained auth in TAMS.

<!-- This is an optional element. Feel free to remove. -->
## Decision Drivers

* Be prescriptive enough to enable interoperability of service and client implementations
* Be permissive enough to facilitate integration with existing workflows and systems
* Acknowledge that organisations will have different threat models, and interoperability should be equally possible in more open and more restrictive environments
* As far as practical, maintain sensible parallels between coarse and fine-grained approaches
* Enable as fine-grained auth as is practical and sensible
* Must be possible to implement the design efficiently

## Considered Options

* Option 1a: Granularity of auth - Source
* Option 1b: Granularity of auth - Flow
* Option 1c: Granularity of auth - Segment
* Option 1d: Granularity of auth - Object
* Option 2a: Level of prescriptiveness - General principles
* Option 2b: Level of prescriptiveness - Auth logic
* Option 2c: Level of prescriptiveness - Specific API requests/pseudocode/scopes
* Option 2d: Level of prescriptiveness - Mandate the use of the proposed approach
* Option 3a: Supported architectures - Deep integration
* Option 3b: Supported architectures - Auth proxy
* Option 4a: Auth attributes - Multiple Tags
* Option 4b: Auth attributes - Single Tag with a list value
* Option 4c: Auth attributes - Specific parameters

## Decision Outcome

Chosen options:

* Option 1b: Granularity of auth - Flow
* Option 2b: Level of prescriptiveness - Auth logic
* Option 3b: Supported architectures - Auth proxy
* Option 4b: Auth attributes - Single Tag with a list value

This combination of options provides a good balance of well defined behaviour and flexibility.
It facilitates both interoperability and integration with existing auth systems and workflows.
The choice of Option 3b does not preclude the solution developed being implemented as described in Option 3a.
The choice of Option 4b allows for us to experiment with, and refine our approach to fine-grained auth.
Once our approach is mature, we may wish to consider migrating to Option 4c to provide a more efficient solution.

### Implementation

Implemented by <https://github.com/bbc/tams/pull/115>.

## Pros and Cons of the Options

### Option 1a: Granularity of auth - Source

Define permissions at the Source level.
Permissions are then propagated down to Flows, Segments, and Objects.

* Good, because it can be implemented with minimal changes to the API specification
* Good, because it requires the least additional data to be stored in/alongside the API
* Bad, because it provides limited control over different representations of media
  * Prevents cost control (e.g. allow access to proxies, but not hi-res)
  * Prevents management of access to specific storage backends

### Option 1b: Granularity of auth - Flow

Define permissions at the Source and Flow levels.
Permissions are then propagated down to Segments, and Objects.
However the default approach should be to define permissions on Sources (since permissions are likely to apply to all renditions of a piece of content), with the option to use Flows where restricting specific variants is required.

* Good, because it can be implemented with minimal changes to the API specification
* Good, because it requires a manageable amount of additional data to be stored in/alongside the API
* Good, because it provides control over different representations of media
* Neutral, because access can only be provided to entire flows
  * Time-scoped access requires new flows to be created, potentially via zero-copy mechanism

### Option 1c: Granularity of auth - Segment

Define permissions at the Source, Flow, and Segment levels.
Permissions are then propagated down to Objects.

* Good, because it can be implemented with minimal changes to the API specification
* Good, because it provides control over different representations of media
* Good, because it enables direct control of access to segments of flow timelines
  * Note that segments may contain multiple video frames/audio samples etc
  * Allowing direct sub-segment access control would require significant further modification
* Bad, because it requires significant amounts of additional data to be stored in/alongside the API

### Option 1d: Granularity of auth - Object

Define permissions at the Source, Flow, Segment, and Object levels.

* Good, because it can be implemented with minimal changes to the API specification
* Good, because it provides control over different representations of media
* Good, because it maps the right to access content onto the content itself, regardless of how it is re-used
* Neutral, because it enables direct control of access to segments of flow timelines
  * Allowing direct sub-segment access control would require significant modification
* Bad, because it requires significant amounts of additional data to be stored in/alongside the API
* Bad, because it may make re-use of media very complicated

### Option 2a: Level of prescriptiveness - General principles

State some general principles implementations may follow, and technologies they may use.
Leave the definition of auth logic etc up to individual implementations.

* Good, because it provides high levels of flexibility in implementations
* Bad, because it makes interoperability around fine-grained auth difficult
* Bad, because it requires implementers to derive all auth logic from scratch, including a few known non-trivial aspects

### Option 2b: Level of prescriptiveness - Auth logic

Define principles, and high-level auth logic.
Leave specific algorithms, and the requests that permissions evaluation systems may make to the API up to the individual implementations.

* Good, because it facilitates interoperability around fine-grained auth
* Good, because implementers don't have to derive auth logic from scratch
* Neutral, because it provides medium levels of flexibility to implementations

### Option 2c: Level of prescriptiveness - Specific API requests/pseudocode/scopes

Define all auth logic, algorithms that evaluate that auth logic, and API requests permission evaluation systems will make.

* Good, because it facilitates interoperability around fine-grained auth
* Good, because implementers don't have to derive auth logic, or algorithms from scratch
* Bad, because it provides low levels of flexibility to implementations
  * This may conflict with existing auth systems, and workflows in deployments and organisational structures and models

### Option 2d: Level of prescriptiveness - Mandate the use of the proposed approach

Make the proposed approach to fine-grained auth mandatory.

* Good, because it ensures full interoperability around fine-grained auth
* Bad, because the approach may conflict with existing auth systems, and workflows in deployments and organisational structures and models
* Bad, because such conflicts being a mandatory part of the specification may prevent/impede use of TAMS by some organisations

### Option 3a: Supported architectures - Deep integration

Assume all TAMS services that support fine-grained auth will implement it with deep integration into the API implementation where policy decisions are made by the store implementation as part of processing a request, with full access to any backing databases etc.

* Good, because its the most efficient option to implement
* Bad, because it provides low levels of flexibility when integrating with existing auth systems, and workflows in deployments

### Option 3b: Supported architectures - Auth proxy

Assume fine-grained auth may be implemented using the Auth Proxy pattern where an HTTP reverse proxy can receive incoming requests, amend them as needed and forward them onto a store (which may have no fine-grained authorisation model).
The proxy can use the contents of the original request, the amended request(s) and the response(s) to make a decision on what to return to the user without modifying the underlying store.

* Good, because it provides high levels of flexibility when integrating with existing auth systems, and workflows in deployments
* Neutral, because its an acceptably efficient option to implement

### Option 4a: Auth attributes - Multiple Tags

Use existing tags implementation to provide/query attributes as part of an Attribute-Based Access Control (ABAC) system.

* Good, because it requires little/no changes to the API specification
* Bad, because it requires un-intuitive use of the existing tag features
* Bad, because it requires multiple API calls when carrying out evaluation of permissions on certain endpoints

### Option 4b: Auth attributes - Single Tag with a list value

Expand the existing tag capabilities to allow lists as values to support an improved ABAC solution.

* Good, because required changes to the API specification are useful beyond fine-grained auth
* Good, because it makes use of tags for this purpose more intuitive
* Good, because it requires very few API calls when carrying out evaluation of permissions on endpoints

### Option 4c: Auth attributes - Specific parameters

Define new parameters throughout the API specification for the purpose of storing auth-specific attributes.

* Good, because it allows for an optimal number API calls when carrying out evaluation of permissions on endpoints
* Neutral, because it results in increased integration of auth mechanisms into the core specification
* Bad, because it requires significant changes to the API specification for a feature that has not been widely tested

## More Information

Information on TAMS' approach to authentication may be found in [ADR0028](./0028-authentication-methods.md).
