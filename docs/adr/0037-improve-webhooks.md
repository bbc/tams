---
status: "proposed"
---
# Proposal for improvements to the Webhooks endpoints

## Context and Problem Statement

Webhooks were added to the TAMS API shortly before it was open-sources.
They have seen some refinement over time, but have only recently started to see significant use.

While carrying out recent work on fine-grained auth it was noticed that AWS' open-source implementation of the API, and BBC R&D's experimental implementation did not match in their interpretation of the primary key for Webhooks.
AWS have used the `url` as the sole primary key.
R&D have used a tuple of `url`, `api_key_name`, and `api_key_value`.
This arrives from a strict reading of the specification on when implementations should update existing Webhooks.
It was noticed that this later interpretation, combined with the hiding of the secret `api_key_value`, could result in multiple Webhooks existing which look otherwise identical.
It was also noticed that as currently defined, the loss of the secret `api_key_value` would prevent the editing or deleting of Webhooks.
Worse, the use of an existing `url` and `api_key_name`, but a different `api_key_value` could unintentionally and opaquely result in the creation of a new Webhook.
Furthermore, it was noted that the current CRUD workflows for Webhooks do not match those elsewhere in the API.
A compelling use case was also identified that is not currently easily implemented.
A client may wish to filter different events in different ways.
For example, they may wish to receive all `flows/created` events, but only `flows/segments_added` for specific flows.

## Decision Drivers

* Decision driver 1: The current specification is ambiguous towards what is the primary key for Webhooks
* Decision driver 2: The current approach can result in Webhooks which are impossible to edit/delete
* Decision driver 3: A strict interpretation of the current specification can result in multiple Webhooks that look identical
* Decision driver 4: The current specification for Webhooks does not follow CRUD workflow patterns elsewhere in the API
* Decision driver 5: The current approach does not easily allow for more complex matrixing of events and filters
* Decision driver 6: The current approach does not allow for direct retrieval of individual Webhooks
* Decision driver 7: Editing/rotating of `api_key_value` currently requires deleting of the existing webhook using the old key, and re-creation with the new key
* Decision driver 8: This part of the API is starting to see increased use

## Considered Options

* 1a Primary key: `url`
* 1b Primary key: Tuple of `url`, `api_key_name`, and `api_key_value`
* 1c Primary key: Tuple of `url` and `api_key_name`
* 1d Primary key: Add a UUID
* 2a Authorization method: Data as a secret
* 2b Authorization method: Use the same auth methods as the rest of the API
* 3a HTTP endpoint structure: Single endpoint
* 3b HTTP endpoint structure: Add a `/service/webhooks/{id}` endpoint
* 4a Registering of Webhooks: Existing POST to `/service/webhooks`
* 4b Registering of Webhooks: POST with `ID` to `/service/webhooks`
* 4c Registering of Webhooks: PUT/POST to `/service/webhooks/{id}`
* 5a Editing of Webhooks: Existing POST to `/service/webhooks`
* 5b Editing of Webhooks: POST with `ID` to `/service/webhooks`
* 5c Editing of Webhooks: PUT/POST to `/service/webhooks/{id}`
* 6a Deleting of Webhooks: Existing POST to `/service/webhooks`
* 6b Deleting of Webhooks: POST with `ID` to `/service/webhooks`
* 6c Deleting of Webhooks: PUT/POST to `/service/webhooks/{id}`
* 6d Deleting of Webhooks: DELETE to `/service/webhooks/{id}`
* 7a Backwards compatibility: Maintain backwards compatibility
* 7b Backwards compatibility: Do not maintain backwards compatibility

## Decision Outcome

Chosen options:

* 1d Primary key: Add a UUID
* 2b Authorization method: Use the same auth methods as the rest of the API
* 3b HTTP endpoint structure: Add a `/service/webhooks/{id}` endpoint
* 4c Registering of Webhooks: PUT/POST to `/service/webhooks/{id}`
* 5c Editing of Webhooks: PUT/POST to `/service/webhooks/{id}`
* 6d Deleting of Webhooks: DELETE to `/service/webhooks/{id}`
* 7b Backwards compatibility: Do not maintain backwards compatibility

### Consequences

* Good, because it brings CRUD workflows for Webhooks into line with other parts of the API
* Good, because it removes ambiguities around managing Webhooks
* Good, because it removes ambiguities from the specification that have been interpreted in multiple ways
* Good, because it prevents Webhooks ending up in a state where they cannot be deleted
* Good, because it prevents accidental creation of duplicate Webhooks
* Good, because it enables more complex Webhooks use cases
* Neutral, because the issues identified necessitate breaking changes anyway, we should take the opportunity to "do things right" while usage is relatively low

### Implementation

{Once the proposal has been implemented, add a link to the relevant PRs here}

## Pros and Cons of the Options

### 1a Primary key: `url`

Use the `url` parameter as the unique primary key for Webhooks.

* Neutral, because this matches one of the most commonly used TAMS server implementations
* Bad, because this this prevents setting of different filters for different event types
* Bad, because combining this with options that add endpoints for specific Webhooks would require escaping of the URL within the parameter

### 1b Primary key: Tuple of `url`, `api_key_name`, and `api_key_value`

The description of the Webhook endpoint currently states the following:

```text
Making a POST request to this endpoint with the same URL, API key name and value but a different list of events SHOULD update the existing registration.
```

The `api_key_name` is a header to be included in events sent to the URL, and that will be set to the secret `api_key_value`.
The API Key serves as a secret that receiving clients may use to authenticate event payloads.
The secret `api_key_value` is never returned in responses from the TAMS instance.

A strict reading of this could be that the tuple of URL, `api_key_name`, and `api_key_value` constitutes the primary key for Webhooks.

* Good, because this matches a strict reading of the spec
* Bad, because the primary key relies on a secret
  * If that secret is lost, the Webhook cannot be edited or deleted
* Bad, because multiple Webhooks could use the same URL and `api_key_name`
  * These Webhooks would look identical in the listing, but be different
* Bad, because this this prevents setting of different filters for different event types
  * While different `api_key_name`'s could be used, but this may clash with the fields intended purpose of providing a consistent means to authenticate events
* Bad, because if the incorrect `api_key_value` is inadvertently used when updating Webhooks, a new one maybe created

### 1c Primary key: Tuple of `url` and `api_key_name`

A modification to prevent accidental duplication of Webhooks would be to only use the URL and `api_key_name` as the identifying tuple.

* Good, because this would not violate the existing wording around when an existing Webhook should be updated
* Good, because it prevents inadvertent creation of duplicate Webhooks
* Good, because the primary key consists only of readable data
* Neutral, because it may be considered a non-breaking change
* Neutral, because if that secret is lost, the wWbhook cannot be edited or deleted without further API changes
* Bad, because this this prevents setting of different filters for different event types
  * While different `api_key_name`'s could be used, but this may clash with the fields intended purpose of providing a consistent means to authenticate events

### 1d Primary key: Add a UUID

This option would add a UUID `id` property which would serve as the unique identifier for Webhooks.

* Good, because it prevents inadvertent creation of duplicate Webhooks
* Good, because the primary key consists only of readable data
* Good, because it is consistent with patterns used elsewhere in the API
* Good, because it allows for multiple Webhooks using the same URL and API Key
  * This would allow for full matrixing of filters and event types
* Neutral, because if that secret is lost, the Webhook cannot be edited or deleted without further API changes
* Bad, because this likely requires breaking changes

### 2a Authorization method: Data as a secret

The description of the Webhook endpoint currently states the following:

```text
Making a POST request to this endpoint with the same URL, API key name and value but a different list of events SHOULD update the existing registration.
```

The secret `api_key_value` is never returned in responses from the TAMS instance.
In practice, this results in the `api_key_value` being used as a means to authorize modification of existing Webhooks.

* Good, because it protects a part of the API which interacts with other systems without requiring full ABAC/RBAC
* Neutral, because the same authorization secret is used in multiple parts of the architecture
* Bad, because loss of the secret `api_key_value` prevents updating/deleting of Webhooks

### 2b Authorization method: Use the same auth methods as the rest of the API

This option would see authorization on the webhooks match the rest of the API.
The specific auth method used will depend on the deployment.
RBAC (Role Based Access Control) is widely used in existing TAMS implementations and fine-grained ABAC (Attribute Based Access Control) approaches are currently in development.

* Good, because it avoids authorisation on the Webhooks endpoint being a special case
* Good, because RBAC is widely used in existing TAMS implementations
* Good, because proposed ABAC approaches would allow for fine-grained access control to individual Webhooks
* Neutral, because fine-grained ABAC with TAMS is still experimental

### 3a HTTP endpoint structure: Single endpoint

This would see the existing Webhook endpoint structure maintained with no changes.

* Good, because it requires no changes
* Bad, because it doesn't follow patterns used elsewhere in the API
* Bad, because it requires overloading of POST for creation, edit, and deletion of Webhooks
* Bad, because it requires the reading of a potentially large listing to read a single Webhook even if it's ID is known

### 3b HTTP endpoint structure: Add a `/service/webhooks/{id}` endpoint

This would add an endpoint for accessing individual Webhooks, akin to `/flows/{flowID}` and `/sources/{sourceID}`.

* Good, because it follows patterns used elsewhere in the API
* Good, because it allows for splitting out of DELETE methods for Webhooks
* Good, because it allows immediate access to specific Webhooks
* Neutral, because it requires a non-breaking change

### 4a Registering of Webhooks: Existing POST to `/service/webhooks`

This would maintain the existing approach to registering Webhooks.
But may result in the API generating an ID and adding it to the return data, if Option 1d is chosen.

* Good, because it doesn't require any changes to the POST request body
* Neutral, because clients may have to handle the new `ID` in the return data
* Bad, because it doesn't match patterns used elsewhere in the API
* Bad, because the current approach has some ambiguities that can lead to a poor user experience

### 4b Registering of Webhooks: POST with `ID` to `/service/webhooks`

This would maintain the existing endpoint for registering Webhooks, but require the specifcation of an ID.

* Good, because it removes ambiguities in the endpoint
* Bad, because its a breaking change
* Bad, because it doesn't match patterns used elsewhere in the API

### 4c Registering of Webhooks: PUT/POST to `/service/webhooks/{id}`

This would use a new endpoint for the creation of Webhooks.

* Good, because it removes ambiguities in the existing endpoint
* Good, because it matches patterns used elsewhere in the API
* Bad, because its a breaking change

### 5a Editing of Webhooks: Existing POST to `/service/webhooks`

This would maintain the existing approach to editing Webhooks without any changes to the request body.

* Good, because it doesn't require any changes
* Bad, because which Webhook a user wishes to edit may be ambiguous
  * This may make this option impossible to implement
* Bad, because it may be ambiguous if a user wishes to create or edit a Webhook
* Bad, because it doesn't match patterns used elsewhere in the API

### 5b Editing of Webhooks: POST with `ID` to `/service/webhooks`

This would maintain the existing endpoint for editing Webhooks, but require the specifcation of an ID.

* Good, because it removes ambiguities over which Webhook is to be edited
* Good, because it removes ambiguities over whether the Webhook is to be edited or created
* Bad, because its a breaking change
* Bad, because it doesn't match patterns used elsewhere in the API

### 5c Editing of Webhooks: PUT/POST to `/service/webhooks/{id}`

This would use a new endpoint for the editing of Webhooks.

* Good, because it removes ambiguities over which Webhook is to be edited
* Good, because it removes ambiguities over whether the Webhook is to be edited or created
* Good, because it matches patterns used elsewhere in the API
* Bad, because its a breaking change

### 6a Deleting of Webhooks: Existing POST to `/service/webhooks`

This would maintain the existing approach to deleting Webhooks without any changes to the request body.

* Good, because it doesn't require any changes
* Bad, because which Webhook a user wishes to delete may be ambiguous
  * This may make this option impossible to implement
* Bad, because it overloads the POST method to enact a delete operation
* Bad, because it doesn't match patterns used elsewhere in the API

### 6b Deleting of Webhooks: POST with `ID` to `/service/webhooks`

This would maintain the existing endpoint for deleting Webhooks, but require the specifcation of an ID.

* Good, because it removes ambiguities over which Webhook is to be deleted
* Bad, because its a breaking change
* Bad, because it overloads the POST method to enact a delete operation
* Bad, because it doesn't match patterns used elsewhere in the API

### 6c Deleting of Webhooks: POST to `/service/webhooks/{id}`

This would use a new endpoint for the deleting of Webhooks, but use the current approach of deleting by removing all events from the Webhook.
This option would require this method to be a POST due to the result of the request not matching the data sent in it.

* Good, because it removes ambiguities over which Webhook is to be deleted
* Bad, because its a breaking change
* Bad, because it prevents users from retaining webhooks (e.g. to retain the keys) but suppressing events
* Bad, because it overloads the PUT/POST method to enact a delete operation
* Bad, because it doesn't match patterns used elsewhere in the API

### 6d Deleting of Webhooks: DELETE to `/service/webhooks/{id}`

This would use a DELETE method on a new endpoint for the deleting of Webhooks.

* Good, because it removes ambiguities over which Webhook is to be deleted
* Good, because it uses an unambiguous DELETE method to enact a delete operation
* Good, because it matches patterns used elsewhere in the API
* Bad, because its a breaking change

### 7a Backwards compatibility: Maintain backwards compatibility

This option would see backwards compatibility maintained with the existing implementation, possibly with deprecation warnings, even if new workflows are added.

* Good, because it maintains backwards compatibility
* Neutral, because breaking changes may be required anyway
* Bad, because it maintains patterns which don't match the rest of the API
* Bad, because some operations may become ambiguous and impossible to fulfil
* Bad, because some existing operations may not actually be possible to implement going forward
* Bad, because it perpetuates workflows that may have unintended results
  * e.g. using the wrong `api_key_value` results in the creation of a new Webhook, instead of editing of an existing one
* Bad, because it may result in multiple possible workflows to achieve the same result

### 7b Backwards compatibility: Do not maintain backwards compatibility

This option would see backwards compatibility broken.

* Good, because it makes Webhooks follow patterns elsewhere in the API
* Good, because it removes all possibilities for ambiguous operations
* Good, because it minimises the number of possible workflows to achieve a given result
* Neutral, because breaking changes may be required anyway
* Bad, because it breaks backwards compatibility
