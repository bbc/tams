---
status: "draft"
---
# Add the ability to query sources without a collected_by value

## Context and Problem Statement

Currently at the Source level there is no filtering on the `collected_by` field.
When vendors are building systems which list content stored in TAMS then they are only looking for the sources at the top of the content tree.
In many cases this is the multi-Source, however due to single essence (eg audio only) workflows then this is not a reliable method of finding the top level content.
To achieve this they must go through every result and look to see if the `collected_by `field is missing as this then indicates that it is the top of a Source collection.
This process can also throw any form of sensible pagination in a client application as when requesting content from the TAMS API it is not known how many results will be retained or discarded.

This ADR is to look at moving this behaviour from the client side into the API.
This has the benefit of not only making it simpler for any system looking for top level content in the system, but also makes the result more predicable as the number of rows requested from the API will result in the available rows up to that limit.

While the focus of this ADR is on the Source level of the TAMS API, there are sufficient similarities between the data structures of sources and flows that it is worth considering whether this should be applied to both levels.


## Considered Options

Source Options:
* Option 1: Follow tags example and use two query parameters for value and exists
* Option 2: Follow tags example but only implement the exists query parameter
* Option 3: Follow accept_get_urls example and use an empty query parameter
* Option 4: Do nothing

Flows:
* Option: Apply the same querying capabilities at both Source and Flow level
* Option: Only apply the new query capabilities at the Source level

## Decision Outcome

tbc

### Implementation

See the API specification changes in PR [#xxx](https://github.com/bbc/tams/pull/xxx).

## Pros and Cons of the Options

### Option 1: Follow tags example and use a collected_by_exists query parameter

When querying tags there are two fields available - you query on a tag name to get the value, or to query on a second parameter (`tag_exists`) to find out if that tag exists.
Following this model would mean adding a two parameters - a new query parameter `collected_by_exists` with a boolean value and the `collected_by` to be able to search on one or more ID's.

For the boolean field setting to false this would return all Sources where there is no `collected_by` values present which is the required behaviour.
Setting this to true would only return Sources which have a `collected_by` value.
This option currently has no uses cases, however using this model and a boolean logically requires this behaviour.


| Behaviour | Query Parameter |
| --------- | --------------- |
| Source is not collected | `collected_by_exists=false` |
| Source is collected by specific Source | `collected_by=a46c49f1-4764-42b9-9f91-f267a58903c4` |
| Source is collected by any of a set of Sources | `collected_by=a46c49f1-4764-42b9-9f91-f267a58903c4,f3ac31bb-c66b-43f8-8362-c82e76f0d28d` |
| Source is collected by any Source | `collected_by_exists=true` |
| Note that this combination is non-sense | `collected_by_exists=false&collected_by=a46c49f1-4764-42b9-9f91-f267a58903c4` |

### Option 2: Follow tags example but only implement the exists query parameter

Since the use cases driving this requirement only focus on whether the item is `collected_by` another Source, then option 2 takes just the exists query parameter element from option 1 and implements that.
In this option it is not possible to query on the ID in the collection, only that it exists.

| Behaviour | Query Parameter |
| --------- | --------------- |
| Source is not collected | `collected_by_exists=false` |
| Source is collected by any Source | `collected_by_exists=true` |


### Option 3: Follow accept_get_urls example and use an empty query parameter

On the `/segments` end point it is possible to specify a query parameter of `accept_get_urls`.
This field can be comma separated list of labels, however it is allowed to be examply which means that the `get_urls` are ommited in the result


| Behaviour | Query Parameter |
| --------- | --------------- |
| Source is not collected | `collected_by=` |
| Source is collected by specific Source | `collected_by=a46c49f1-4764-42b9-9f91-f267a58903c4` |
| Source is collected by any of a set of Sources | `collected_by=a46c49f1-4764-42b9-9f91-f267a58903c4,f3ac31bb-c66b-43f8-8362-c82e76f0d28d` |
| Source is collected by any Source |  Not possible |

If chosen to also apply at the Flow leve then is `collected_by=a46c49f1-4764-42b9-9f91-f267a58903c4` too similar to `/flows/a46c49f1-4764-42b9-9f91-f267a58903c4/flow_collection`? 
The first gives you all the metadata about the flows, where the later only gives you the ID's and roles

