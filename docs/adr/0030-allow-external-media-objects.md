---
status: "proposed"
---
# Allow External Media Objects

## Context and Problem Statement

The TAMS API currently requires that Flow Segments registered through the `/flows/{flow-id}/segments` endpoint reference media objects that were uploaded to a location provided by the `/flows/{flow-id}/storage` endpoint.
This requirement prevents TAMS from referencing media objects that are stored elsewhere, including media objects from other Flows.
This requirement also forces copy transfers and duplication of media objects which is undesirable.

## Considered Options

* Option 1: Keep the current media object storage requirements
* Option 2: Loosen the requirement to allow references to existing media objects from other Flows
* Option 3: Loosen the requirement to allow references to external media objects

## Decision Outcome

Chosen option: Option 2 and 3, because object reuse is already assumed to work across Flows and external media objects is likely to be a requirement when using some form of storage federation.
A TAMS implementation can still limit which media objects can be referenced if it wants to.

### Implementation

See the API specification changes in PR [#118](https://github.com/bbc/tams/pull/118).

## Pros and Cons of the Options

### Option 1: Keep the current media object storage requirements

* Good, because it means there is no specification change
* Bad, because it contradicts the object reuse requirement and expectation that references to media objects in other Flows is supported
* Bad, because it prevents any form of federation of storage and requires copy transfers to be made

### Option 2: Loosen the requirement to allow references to existing media objects from other Flows

Media object reuse is expected to allow reuse across Flows.
This change is essentially a fix of the specification rather than a feature or breaking change.

This option still requires that a *new* media object is only stored in a location provided by the Flow referencing the media object's `/flows/{flow-id}/storage` endpoint.
This essentially means that the *new* media object can't be stored in a location that was not intended for the Flow.
This could be another Flow's intended location or a random location that a client has decided to use.

* Good, because it allows media object reuse as designed
* Neutral, because TAMS implementations would no longer need to enforce which location was used if the Flow Segment references an existing media object
* Neutral, because clients can no longer rely on all TAMS instances to enforce a single Flow media object access control

### Option 3: Loosen the requirement to allow references to external media objects

The media objects could be held in other storage locations.
The requirement is loosened so that clients don't need to copy the media objects across to the storage provided by the TAMS instance.
It also avoids having multiple copies of the same media objects which can complicate management of those media objects.

The TAMS would need to have information about the media object to provide access to clients.
This information could be provided in the Flow Segment's `get_urls` by the client that registers the Flow Segment.
Another possibility is that the media object ID includes a component that informs the TAMS where the media objects is stored and how to access it.
E.g. the media object ID could be a URI that provides a location component that is populated for external media objects.

Recommendations for handling external media objects and federation are expected to be made in future ADRs and Appnotes.
These recommendations would extend the [Referencing TAMS content in other systems](../appnotes/0014-referencing-tams-content-in-other-systems.md) Appnote that focusses on Flow and Source level references.
The [Source-level Edit](../adr/0024-source-level-edit.md) ADR proposes exploration for more direct by-reference operations and this may also include support for referencing external media objects.

* Good, because it allows references to media objects in other locations
* Neutral, because TAMS implementations may to need know by some means how to handle when no more references are made to the media object, e.g. inform the external storage that the media object is no longer referenced by the target TAMS and can be deleted
