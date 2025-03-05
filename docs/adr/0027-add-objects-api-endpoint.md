---
status: "proposed"
---
# Add an objects API endpoint

## Context and Problem Statement

There is a requirement to identify all Flows that reference (via a Flow Segment) a particular media object.
This for example supports a business or legal requirement to delete a media object from the store, which requires knowing which Flows reference it.
The media object can be deleted by deleting all (Flow Segment) references to it.

The proposal is to add a `/objects?object_id={object-id}` endpoint that provides a list of Flows that reference (via Flow Segments) the media object.

## Considered Options

* Option 1: Use the existing endpoints to discover which Flows reference a media object
* Option 2: Add a `/objects?object_id={object-id}` endpoint that lists all Flows that reference a media object
* Option 3a: Extend 2 to optionally signal which Flow first referenced the media object in the TAMS instance
* Option 3b: Restrict 3a to require signalling which Flow referenced the media object first
* Option 3c: Allow a user to set `first_referenced_by_flow`
* Option 4: Add an endpoint to list media objects for a Flow

## Decision Outcome

Chosen option: Option 3a, because it is a more efficient way to discover which Flows reference a media object and knowing the first reference may help trace the origin of the media object.
Is there a need to always have the information available and therefore make the property required, i.e. choose option 3b?

### Implementation

The specification changes have been implemented in PR [#111](https://github.com/bbc/tams/pull/111).

## Pros and Cons of the Options

### Option 1: Use the existing endpoints to discover which Flows reference a media object

The Flows (and Flow Segments) referencing a media object can be found by using a GET of `/flows/{flow-id}/segments?object_id={object-id}` for every Flow.

* Good, because there are no changes to the API
* Bad, because it requires a client to loop through all the Flows to GET the Flow Segments that reference the media object
* Bad, because it is likely more efficient for TAMS to be asked to run a single query across all Flows then to run multiple queries for each Flow in turn

### Option 2: Add a `/objects?object_id={object-id}` endpoint that lists all Flows that reference a media object

This `/objects?object_id={object-id}` endpoint provides JSON that lists of all Flows referencing a media object.
The `referenced_by_flows` property contains the list of Flow IDs.

The Flow Segments that reference the media object can all be found using a GET on `/flows/{flow-id}/segments?object_id={object-id}` for every Flow in the listing rather than every Flow.
The Flow Segments that reference the media object can all be deleted using a DELETE on `/flows/{flow-id}/segments?object_id={object-id}` for every Flow in the listing.

The `object_id` is as a query parameter rather than a URL path component because the media object ID structure is not restricted.
For example, the `/` character is likely to be used where the object identifiers follow a file-system-like naming structure and it clashes with the use of `/` in the HTTP URL structure.

The `/objects?object_id={object-id}` endpoint does not allow a GET of all media objects; the `object_id` query parameter is required.

The `/objects?object_id={object-id}` endpoint does not allow a POST or PUT to register a media object.
A media object can only registered in TAMS as part of Flow Segment registration.

The `/objects?object_id={object-id}` endpoint does not allow a DELETE of a media object.
A media object is only deleted in TAMS after all Flow Segments referencing the media object have been deleted.
This allows Flow-level permissions to be used to restrict which Flow Segments can be deleted and ultimately whether the media object can be deleted.

* Good, because it is a more efficient way to discover which Flows reference a media object
* Good, because it supports Flow-level access permissions
* Neutral, because it requires further requests to discover which Flow Segments reference the media object

### Option 3a: Extend 2 to optionally signal which Flow first referenced the media object in the TAMS instance

It may be useful to know which Flow was the first to reference the media object in the TAMS instance.
This could help determine the origins of the media object.

An optional `first_referenced_by_flow` property is added to the `/objects?object_id={object-id}` resource that contains the Flow ID.

The Flow ID in `first_referenced_by_flow` is set by the TAMS instance and is not settable by a user.

The TAMS instance should set the property to the first Flow that had a new Flow Segment created that referenced the media object.
The TAMS instance should also include the Flow ID in the `referenced_by_flows` property if the Flow exists in the TAMS and has a Flow Segment referencing the media object.
The TAMS instance may either remove or keep the property if the first Flow or the Flow Segments referencing the media object in the first Flow are deleted.

* Good, because it retains some information that could be used to trace the origins of a media object
* Neutral, because it allows a TAMS instance to decide whether to always keep the property set or not set the property at all
* Bad, because a user can't set the value and it only reports the origins according to the TAMS instance

### Option 3b: Restrict 3a to require signalling which Flow referenced the media object first

This option restricts 3a to require the `first_referenced_by_flow` to be always be set and retain its value.

* Good, because users can rely on the property being set and the value not changing
* Neutral, because it could reference a Flow that no longer exists
* Neutral, because it requires a TAMS to record which Flow first referenced a media object

### Option 3c: Allow a user to set `first_referenced_by_flow`

This options allows a user to set `first_referenced_by_flow` to provide potentially different information about the origins of the media object.
The Flow ID could be external to the TAMS instance and therefore signal the origin being elsewhere.

* Good, because it could provide information that better informs about the origins of the media object
* Bad, because it loses the information about which Flow in the TAMS instance was the first to reference the media object.
Should a different property be provided for users to set?

### Option 4: Add an endpoint to list media objects for a Flow

The `/flows/{flow-id}/segments` endpoint may not provide an efficient way to get a listing of media objects if there are a lot less media objects than Flow Segments.
This option would add a `/flows/{flow-id}/objects` endpoint for listing media objects for a Flow.
This would require an index to hold a unique set of media objects for a Flow to avoid duplicates in a paged listing.

* Good, because it allows getting a list of media objects for a Flow
* Neutral, because it is unclear whether there are practical examples of large reuse of media objects in single Flow
* Bad, because there is no clear requirement to list media objects rather than Flow Segments
