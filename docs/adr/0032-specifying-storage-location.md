---
status: "proposed"
---
# Specifying storage location when requesting storage allocation

## Context and Problem Statement

The TAMS API supports the referencing of multiple storage locations for Flow Segments in the [`get_urls`](https://bbc.github.io/tams/main/index.html#/operations/GET_flows-flowId-segments#response-body) list.
Properties of these locations may be signalled in the label as per [Application Note 0009](https://github.com/bbc/tams/blob/main/docs/appnotes/0009-storage-label-format.md).
The support for multiple locations in `get_urls` was initially created to allow reference to locations outside of a given TAMS deployment (e.g. in another TAMS deployment, or another system entirely).
The [allocation of storage](https://bbc.github.io/tams/main/index.html#/operations/POST_flows-flowId-storage) by a TAMS instance does not currently make any provisions for multiple storage locations.
It currently is up to the TAMS implementation how and where to allocate storage.

Some deployments may want to provide multiple storage endpoints - for security, cost allocation, tiered storage, or other reasons.
This ADR explores options for how this may be implemented.
Note that this ADR relates only to how clients may choose where storage will be allocated.
This ADR is not proposing any changes to how uploaded content is registered against Flow Segments.
This ADR is not proposing how multiple TAMS instances may peer with each other.

## Decision Drivers

* Add support for multiple storage backends
  * Enable new methods of cost allocation in deployments
  * Enable further methods of authorising access to content (e.g. restrict access to specific storage backends)
  * Enable tiered storage (though movement of content between those tiers would not currently be defined in the spec)
* Unify references to storage types across the spec
  * Storage backends are currently referenced in the [AppNote0009](https://github.com/bbc/tams/blob/main/docs/appnotes/0009-storage-label-format.md) label structure, and the `media_store` parameter at the `/service` endpoint in different ways
  * This ADR would result in the addition of further references when selecting storage backends when allocation storage
* Fulfil the elevation of the components of the [AppNote0009](https://github.com/bbc/tams/blob/main/docs/appnotes/0009-storage-label-format.md) label structure to the core API as planned in [ADR0021](https://github.com/bbc/tams/blob/main/docs/adr/0021-storage-label-format.md)
* Avoid further potential breaking changes to references to storage backends if the elevation of the components of the [AppNote0009](https://github.com/bbc/tams/blob/main/docs/appnotes/0009-storage-label-format.md) label structure to the core API happened at a later date

## Considered Options

* Option 1a: Multiple separate TAMS instances using the existing API with no changes
* Option 1b: Update the TAMS API to allow storage location to be specified when requestion storage allocation
* Option 2a: Specify storage location using the [AppNote0009](https://github.com/bbc/tams/blob/main/docs/appnotes/0009-storage-label-format.md) label structure
* Option 2b: Specify storage location using the storeName portion of [AppNote0009](https://github.com/bbc/tams/blob/main/docs/appnotes/0009-storage-label-format.md) label structure
* Option 2c: Specify storage location using something other than the label
* Option 3a: Configure storage locations out-of-band
* Option 3b: Expand `media_store` parameter at the `/service` endpoint to advertise available storage names
* Option 3C: Expand `media_store` parameter at the `/service` endpoint to advertise available storage names, with storage metadata
* Option 4a: Don't modify approach to `get_urls` `label`
* Option 4b: Elevate the components of [AppNote0009](https://github.com/bbc/tams/blob/main/docs/appnotes/0009-storage-label-format.md) label structure to core spec

## Decision Outcome

Chosen options:

* Option 1b: Update the TAMS API to allow storage location to be specified when requestion storage allocation
* Option 2b: Specify storage location using the storeName portion of [AppNote0009](https://github.com/bbc/tams/blob/main/docs/appnotes/0009-storage-label-format.md) label structure
* Option 3C: Expand `media_store` parameter at the `/service` endpoint to advertise available storage names, with storage metadata
* Option 4b: Elevate the components of [AppNote0009](https://github.com/bbc/tams/blob/main/docs/appnotes/0009-storage-label-format.md) label structure to core spec

Supersede [ADR0021](https://github.com/bbc/tams/blob/main/docs/adr/0021-storage-label-format.md)
Deprecate [AppNote0009](https://github.com/bbc/tams/blob/main/docs/appnotes/0009-storage-label-format.md)

### Consequences

* Good, because references to storage backends will be unified
* Good, because it enables workflows that require multiple storage backends (e.g. tiered storage)
* Bad, because it will result in a breaking change

<!-- This is an optional element. Feel free to remove. -->
### Implementation

{Once the proposal has been implemented, add a link to the relevant PRs here}

## Pros and Cons of the Options

### Option 1a: Multiple separate TAMS instances using the existing API with no changes

Clients are currently able to interact with multiple TAMS instances, as they would with multiple instances of any other API.
Each instance could be associated with an specific storage type/location.
Clients may request the allocation of storage or specific type/location from the relevant TAMS instance which controls it, and uploaded content to it.
The client may then register that content against Flow Segments on multiple TAMS instances, if required for discoverability.
But the lifecycle of those objects registered to a TAMS instance which doesn't control them - in particular deletion and generation of pre-signed URLs where required - would currently have to be handled by the client, or an off-spec extension.
Alternatively, the instances may peer with each other to share content.
How peering may work is outside of the scope of this ADR.
This option also requires the running of duplicate services where they might not otherwise be needed.
This option may also imped the discovery and re-use of content across TAMS instances.

* Good, because it doesn't require a spec change
* Neutral, because clients may have to be able to communicate with multiple TAMS instances anyway when crossing business boundaries
* Bad, because resource use is poor
* Bad, because it relies on off-spec management of the lifecycle of Objects in some cases
* Bad, because it requires clients to communicate with multiple TAMS instances for more use cases
* Bad, because it impedes zero-copy re-use of Segments

### Option 1b: Update the TAMS API to allow storage location to be specified when requestion storage allocation

Clients would be able to specify their required storage location when requesting the allocation of storage.
Clients supporting this feature would manage multiple storage layers for different technical/business purposes such as cost allocation, tiered storage, geographical location etc.
For consistency, this should take the form of an additional parameter in the request body for `/storage` POST requests.

* Good, because it reduces the content-management burden on clients
* Good, because it provides clear responsibility for the lifecycle management of Objects
* Good, because content discoverability and re-use matches current single-instance TAMS use
* Good, because it reduces the number of use-cases that require clients to communicate with multiple TAMS instances
* Neutral, because clients may have to be able to communicate with multiple TAMS instances anyway when crossing business boundaries
* Neutral, because it requires a backwards-compatible spec change
* Bad, because it adds complexity to TAMS instances which support this feature

### Option 2a: Specify storage location using the [AppNote0009](https://github.com/bbc/tams/blob/main/docs/appnotes/0009-storage-label-format.md) label structure

[AppNote0009](https://github.com/bbc/tams/blob/main/docs/appnotes/0009-storage-label-format.md) describes a structured string format for describing storage location, type, and name.
This Application Note used the existing `get_urls` `label` property to test the usefulness of its components without the potential breaking changes of parameters specified in the API itself.
The intention, as stated in [ADR0021](https://github.com/bbc/tams/blob/main/docs/adr/0021-storage-label-format.md), is that the components of these labels will be elevated to the core spec once they are considered stable.
This means any use of this label structure for the purpose of specifying storage locations would likely require a breaking change in the part of the spec defining that specification once the elevation of that change happens.
Additionally, the core spec doesn't currently require the use of AppNote0009 label structures.
That said, AppNote0009 is currently the only strongly defined method of referring to storage locations.

* Good, because it re-uses an existing structured label format for storage
* Neutral, because it is very verbose
* Bad, because it will likely require a future breaking change

### Option 2b: Specify storage location using the storeName portion of [AppNote0009](https://github.com/bbc/tams/blob/main/docs/appnotes/0009-storage-label-format.md) label structure

A small modification to [AppNote0009](https://github.com/bbc/tams/blob/main/docs/appnotes/0009-storage-label-format.md) would be to require the `storeName` component of the `label` to be unique to a given storage location.
This likely matches expected behaviour and current use.
It would allow for the specification of storage locations using only that component.
This would also likely mean that the location specification aspect of the API spec wouldn't have to be modified once the `get_urls` `label` components are elevated to the core spec.
This has the downside that the core spec doesn't currently require the use of AppNote0009 labels.

* Good, because it should avoid a future breaking change
* Neutral, because it is less verbose than the full [AppNote0009](https://github.com/bbc/tams/blob/main/docs/appnotes/0009-storage-label-format.md) format
* Bad, because it would currently differ in format to `get_urls` `labels` (This bad point would be negated if we also choose Option 4b)

### Option 2c: Specify storage location using something other than the label

The spec doesn't currently require the use of the [AppNote0009](https://github.com/bbc/tams/blob/main/docs/appnotes/0009-storage-label-format.md) label format.
It doesn't even require use of consistent labels for a given store.
This option is to maintain the separation of store and label.
The storage location would be specified with a new for-purpose separate reference.

* Good, because it would likely avoid a future breaking change in this part of the store
* Neutral, because it would be less verbose than the full [AppNote0009](https://github.com/bbc/tams/blob/main/docs/appnotes/0009-storage-label-format.md) format
* Bad, because it would currently differ in format to `get_urls` `labels`, which currently has a similar purpose
* Bad, because it may require further mapping to `get_urls` `labels` to be useful

### Option 3a: Configure storage locations out-of-band

Whatever representation is used for specifying the location of storage, a common understanding of storage names and the storage they refer to is required for a TAMS service instance and its clients.
Users deploying TAMS systems are likely to have significant control of the TAMS service, clients, or both.
This option assumes that one or both of server/clients may have their store names configured on deployment.

* Good, because it doesn't require a change to the API Spec
* Neutral, because integration engineers may need to configure these things manually at deployment anyway
* Bad, because it requires more work by integration engineers for more use cases
* Bad, because it could result in proprietary solutions

### Option 3b: Expand `media_store` parameter at the `/service` endpoint to advertise available storage names

This option is to advertise a list of available storage names that may be used by the client at the `/service` endpoint.
The `media_store` parameter at this endpoint currently provides a simplistic description of the type of storage the store will allocate.
This parameter pre-dates [AppNote0009](https://github.com/bbc/tams/blob/main/docs/appnotes/0009-storage-label-format.md) and provides far less information.
The parameter could be re-purposed and expanded to provide list of storage names available in the simplest case.
It is worth noting that this endpoint should only advertise storage names that the TAMS instance can allocate and manage.
It is possible to register `get_urls` to Segments which are external to the TAMS instance.
This option would not alter that feature.
This option would, in principle, allow for storage types to be added/removed without re-deploying the service.
But this ADR does not specify how this should be implemented.

* Good, because it enables a level of automatic configuration of this behaviour between servers and clients - at least in advertising available stores to users
* Neutral, because this would be a breaking change in a lesser used part of the API
* Bad, because it provides limited information for choosing the best store - particularly through automated mechanisms

### Option 3C: Expand `media_store` parameter at the `/service` endpoint to advertise available storage names, with storage metadata

As with Option 3b, but with a dict providing the metadata currently available in [AppNote0009](https://github.com/bbc/tams/blob/main/docs/appnotes/0009-storage-label-format.md) `get_urls` labels.

* Good, because it enables automatic configuration of this behaviour between servers and clients
* Good, because it provides enough technical metadata to automate the choosing of stores in some cases
* Neutral, because this would be a breaking change in a lesser used part of the API
* Bad, because it would currently differ in format to `get_urls` `labels` and would pre-empt what changes the future breaking change to elevate label parameters to the core API would look like (This bad point would be negated if we also choose Option 4b)

### Option 4a: Don't modify approach to `get_urls` `label`

Currently, the `get_urls` `label` field is a free-text string.
[AppNote0009](https://github.com/bbc/tams/blob/main/docs/appnotes/0009-storage-label-format.md) recommends a structure which includes useful information such as storage type, provider, and location.
This option is to maintain the current approach with no changes.

* Good, because it doesn't require an API change
* Good, because it provides further time to validate the components in [AppNote0009](https://github.com/bbc/tams/blob/main/docs/appnotes/0009-storage-label-format.md) labels
* Neutral, because it pushes out a breaking change we expect to make in future further
* Bad, because it would potentially lead to references to storage locations at the `/service` endpoint and when requesting allocation being formatted differently, depending on what other Options are chosen

### Option 4b: Elevate the components of [AppNote0009](https://github.com/bbc/tams/blob/main/docs/appnotes/0009-storage-label-format.md) label structure to core spec

[ADR0021](https://github.com/bbc/tams/blob/main/docs/adr/0021-storage-label-format.md) resulted in the creation of [AppNote0009](https://github.com/bbc/tams/blob/main/docs/appnotes/0009-storage-label-format.md) as a means to convey additional information about storage in the `get_urls` `label` field.
ADR0021 intended the use of AppNote0009 labels as a temporary solution to validate the useful of the components contained within it, and that a later change would elevate the components to the core spec.
As mentioned in Option 2a and 2b, the addition of the ability to specify storage locations for allocations crosses over with this capability.
In adding the ability to specify storage locations we either have to work to AppNote0009 and expect a future breaking change, pre-empt what the superseding solution to ADR0021 would look like, or implement that superseding solution alongside the storage location specification support.
This option is to make that superseding solution now alongside the ability to specify storage locations.

* Good, because it will unify the references to storage at the `/service`, `get_urls`, and `/storage` parts of the API
* Good, because it would better support multiple storage backends (including tiered storage)
* Bad, because it's a (potentially) breaking change to a core part of the API, though one we have been planning to make for some time
