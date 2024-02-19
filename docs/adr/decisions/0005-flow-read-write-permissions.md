---
status: "accepted"
---
# Flow Read-Write Permissions

## Context and Problem Statement

A Flow read-only permission could be set to protect the Flow from unintended changes to the metadata, Flow Segments and media objects once it is complete.
This is a very basic form of access permissions for Flows that could be extended in future to include things such as users, roles, projects etc.

## Decision Drivers

* Balance providing useful features and avoiding complexity in the TAMS design

## Considered Options

* Option 1: Rely on users to not update a Flow
* Option 2: Add a boolean `read_only` property to set whether updates are permitted or not
* Option 3: Design a more extensive permissions model

## Decision Outcome

Chosen option: Option 2: Add a boolean `read_only` property to set whether updates are permitted or not.

Option 2 was agreed to be a sensible stopgap, to provide some protection against unintended mistakes without adding undue complexity.

### Implementation

TBD

## Pros and Cons of the Options

### Option 1: Rely on users to not update a Flow

This is the current state.

* Good, because the implementation doesn't need to determine whether a request is permitted or not
* Bad, because Flows can easily be updated unintentionally

### Option 2: Add a boolean `read_only` property to set whether updates are permitted or not

If the `read_only` property is set to `true` then the implementation will reject attempts to update the Flow metadata or Flow Segments.
If the `read_only` property is handled by the media object storage as well then it would also reject attempts to update the media objects (e.g. deleting media objects or bypassing the `/storage` endpoint to write media objects).

* Good, because it allows unintentional changes to be prevented
* Bad, because users are still allowed to change the `read_only` property and then make updates
* Bad, because users could still make changes to media objects if the storage doesn't handle the `read_only` property

### Option 3: Design a more extensive permissions model

* Good, because it allow finer grained control of which users can make updates
* Bad, because it adds complexity to the store and requires design work

## More Information

### TAMS/AWS Workshop Discussion - 13th February 2024

A discussion about this proposal took place during the TAMS/AWS workshop on 13th February 2024, with the BBC R&D TAMS team, BBC B&EUT architects and AWS Solution Architects.

This discussion quickly concluded that Option 3 was the ideal, but requires considerable research and consideration, some of which may not be possible without a broader understanding of real world use cases.
Option 2 was agreed to be a sensible stopgap, to provide some protection against unintended mistakes without adding undue complexity.
