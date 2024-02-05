---
status: "proposed"
---
# Created and Modified Timestamps should be managed internally

## Context and Problem Statement

Flows (and Sources if [ADR 002](./0002-add-sources-to-api.md) is accepted) have fields indicating when they were created and last modified, however the API specification and schemas are not clear on whether these fields can be modified by a client, or whether they are exclusively managed by the server.

See [schemas/flow-core.json](../../../api/schemas/flow-core.json) for definitions of those fields.
They exist primarily to make it easier to find items of interest in the API and support engineering functions such as application development and debugging.

## Considered Options

* Option 1: Allow clients to change the dates when making a PUT request
* Option 2: Ignore the date-time values in client requests

## Decision Outcome

Chosen option: Option 2 - Ignore the date-time values in client requests, because it allows users to trust the behaviour of the date-time values, which is important given their primary purpose is to support development and debugging.

### Implementation

Implemented by <https://github.com/bbc/tams/pull/19>

## Pros and Cons of the Options

### Option 1: Allow clients to change the dates when making a PUT request

When making a PUT request, e.g. to `PUT /flows/<flowId>` a client should include a value for each of the `created`, `metadata_updated` and `segments_updated` date-time fields.
The `created` field may correspond to something other than when the Flow was created in this store, for example if it was copied from elsewhere.
The `metadata_updated` field must be the current time if the request modifies the metadata, and `segments_updated` should correspond to when the segments were last updated (which may differ from the time currently in the API, if the client knows better.)

* Good, because it allows multiple stores to hold the same Flow and keep the fields in sync
* Bad, because the date-time values can no longer be trusted for their original purpose if a client can accidentally modify them
* Bad, because it creates additional complexity for the client to provide valid values
* Bad, because it is difficult for the server to validate that values supplied by the client are permissible

### Option 2: Ignore the date-time values in client requests

When making a PUT request, e.g. to `PUT /flows/<flowId>`, values supplied for each of the `created`, `metadata_updated` and `segments_updated` date-time fields are accepted but silently ignored.
Instead, the server sets the `created` time when the Flow is first created on the API, and decides to update `metadata_updated` and `segments_updated` based on other requests made by clients.

* Good, because the date-time values can be trusted to accurately represent the last time things changed on this particular store
* Good, because the implementation is fairly simple
* Bad, because it slightly breaks the expectations of a RESTful PUT, that a resource will be replaced
