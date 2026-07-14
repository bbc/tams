---
status: "proposed"
---
# Options for specifying the sorting of listings

## Context and Problem Statement

The TAMS specification doesn't currently specify how resources should be sorted on some listing endpoints.
These endpoints are:

* `/service/storage-backends`
* `/service/webhooks`
* `/sources`
* `/flows`
* `/flow-delete-requests`

Service implementations currently use a variety of keys to sort these listings such as `created`, `id`, or random ordering.
In some cases, this could result in Clients having to retrieve large numbers of paged results to find items of interest.

Note that the sorting of `/flows/{flowId}/segments` has always been implied to be by `timerange`.
This was recently clarified in [PR 223](https://github.com/bbc/tams/pull/223).
As such, it is not included in this ADR.

## Considered Options

* Option 1 - Don't specify sorting of listings
* Option 2 - Define a single key all implementations should sort listings by
* Option 3 - Define a set list of sorting keys clients may select from
* Option 4 - Allow clients to select any resource parameters to sort by

## Decision Outcome

Chosen option: "Option 3 - Define a set list of sorting keys clients may select from".
Although some endpoints only have a single obvious option for sorting.
These will use "Option 2 - Define a single key all implementations should sort listings by".
This provides the most clarity and flexibility to implementations without placing undue burden to Service implementations.
All endpoints will have a `reverse_order` query parameter, matching that which currently exists on the `/flows/{flowId}/segments` endpoint.

Datetime keys shall be sorted newest-first by default.
String keys shall be sorted ascending alphabetically by default.

The available sorting keys for each endpoint shall be:

* `/service/storage-backends`
  * `label` (only option)
* `/service/webhooks`
  * `url` (only option)
* `/sources`
  * `created` (default)
  * `updated`
  * `label`
* `/flows`
  * `created` (default)
  * `metadata_updated`
  * `label`
* `/flow-delete-requests`
  * `created` (default)
  * `expiry`

Note that the `/flows` endpoint will not allow sorting on `segments_updated` or `timerange`, and the `/flow-delete-requests` endpoint will not allow sorting on `updated`.
This is due to those parameters updating very frequently in many cases.
This would likely lead to the order of the the more recent values behaving erratically.
Consider a deployment with a large number of live ingests.
The first few pages of results ordered by `segments_updated` newest first would essentially be non-deterministic.
Clients wishing to query Flows with recently updated segments should instead use the available filters to select for recently/currently ingesting Flows, and sort by some other appropriate parameter.

### Implementation

Implemented in [PR 224](https://github.com/bbc/tams/pull/224).

## Pros and Cons of the Options

### Option 1 - Don't specify sorting of listings

This option would maintain the current situation where the approach to sorting resource listings isn't specified.

* Good, because it requires no changes to the API specification
* Bad, because sorting behaviour varies between Service implementations
* Bad, because Client implementations must handle arbitrary sortings
* Bad, because Clients may have to search through large numbers of resources to find those they are interested in

### Option 2 - Define a single key all implementations should sort listings by

This option would see a single key defined for listings to be sorted by.

* Good, because sorting behaviour would be consistent between Service implementations
* Good, because Client implementations would have clear expectations of listing sortings
* Good, because a properly chosen key should reduce the number of pages of resources Clients must search through in many cases
* Bad, because Clients may still have to search through large numbers of resources in some cases
* Neutral, because it requires a change to the API specification

### Option 3 - Define a set list of sorting keys clients may select from

This option would see a query parameter provided with which Clients may specify the key by which listings should be sorted.
This query parameter would provide a small number of keys as options which have been identified as useful to sort by.

* Good, because sorting behaviour would be consistent between Service implementations
* Good, because Client implementations would have clear expectations of listing sortings
* Good, because this should reduce the number of pages of resources Clients must search through in most cases
* Neutral, because Clients may still have to search through large numbers of resources in a small number of cases
* Neutral, because it requires a change to the API specification

### Option 4 - Allow clients to select any resource parameters to sort by

As with Option 3, but the clients may select any resource parameter as the sort key.

As with Option 3, plus:

* Neutral, as the benefits of such a generic approach are unclear
* Bad, because Service implementations may be significantly more complicated than with other options
