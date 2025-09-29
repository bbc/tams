---
status: "proposed"
---
# Tag Usability Enhancements

## Context and Problem Statement

TAMS provides tags on Flows and Sources as an ad-hoc key-value store of data.
This enables some simple workflows without the need for an additional database of content, simply by using the TAMS API.
It also enables simpler interoperability, in cases where the tag store is enough to locate the content required in TAMS using e.g. a panel in a tool, rather than an integration with some other MAM.
Over the course of other work on TAMS (notably the exploration of fine-grained authorisation) it has become clear that some improvements to tags would be useful.

## Considered Options

* Option 1a: Add support for lists in tags
* Option 1b: Add support for lists in tags, require every item match
* Option 1c: Add support for lists in tags, add a query for all items matching
* Option 2: Make it possible to filter object instances on tags
* Option 3: Add tags to webhooks

## Decision Outcome

Chosen options:

* Option 1a: Add support for lists in tags
* Option 2: Make it possible to filter object instances on tags
* Option 3: Add tags to webhooks

Option 1a is chosen at present because there is no clear need for Option 1c, but it may be added in future without a breaking change to client implementations.

Options 2 and 3 make the support and behaviour of tags uniform across Flows, Sources, Object Instances and Webhooks.

### Implementation

Implemented by <https://github.com/bbc/tams/pull/153>

## Pros and Cons of the Options

### Option 1a: Add support for lists in tags

Add the option that the value of a tag either be a string, or a list.
Where tags are queryable, make the `tag.{name}` query parameter accept a comma separated list of strings, and require that at least one item in the query matches at least one of the values in the list to return the resource.

* Good, because it makes tags usable for cases when multiple options are present (e.g. authorisation attributes)
* Good, because it improves discoverability of well-tagged resources
* Good, because it allows for finding e.g. a Flow with any of a specific property in a list ("OR" queries)
* Bad, because it makes implementations more complex to handle checking lists in queries
* Bad, because it encourages more usage of TAMS as a MAM

### Option 1b: Add support for lists in tags, require every item match

As in Option 1a, however the `tag.{name}` query parameter requires that every item in the given list matches.

* Good, because it enables queries finding e.g. a Flow with a number of properties ("AND" queries)
* Bad, because it requires knowing the precise list to query it using tags

### Option 1c: Add support for lists in tags, add a query for all items matching

As in Option 1a, with the addition of a `tag_every.{name}` query parameter where every item in the given list matches.

* Good, because it enables both "AND" and "OR" queries
* Good, because it makes the tag query mechanism more complete
* Bad, because it adds another query parameter to implement
* Bad, because at the time of writing there is no concrete use case for "AND" queries
* Bad, because it encourages more usage of TAMS as a MAM

### Option 2: Make it possible to filter object instances on tags

Add `flow_tag.{name}` and `flow_tag.{exists}` to the `GET /objects/{objectId}` endpoint, to adjust the contents of the `referenced_by_flows` list down to a specific subset of Flows.

* Good, because it avoids excessive pagination if an object is used by a very large number of Flows
* Good, because it enables the option to use tags to restrict access to Flows and associated objects
* Neutral, because it requires a change to specification and implementation
* Bad, because it encourages more usage of TAMS as a MAM

### Option 3: Add tags to webhooks

Add tags and tag-based querying to webhooks, in the same was as Flows and Sources.

* Good, because it improves the ability of clients to manage large numbers of webhooks by locating them using tags
* Good, because it enables the option to use tags to restrict access to webhooks
