---
status: "proposed"
---
# Deletion of Content and IDs

## Context and Problem Statement

When a Flow or Source is deleted, the concept of the content still exists and is still tied to the ID, even if the essence does not.
The TAMS approach should recognise and provide a way to avoid all reference to a piece of content ceasing to exist due to e.g. overzealous cleanup by an operator.

## Decision Drivers

* It should be possible to identify that content once existed for audit purposes, even if subsequently deleted
* The conceptual content model holds that Source and Flow IDs are immutable - it follows that an ID still applies to a piece of content even after deletion

## Considered Options

* Option 1: Assume DELETE requests will be mediated by other systems, accept all requests
* Option 2: Add `is_deleted` flag on Sources and Flows
* Option 3: Allow Flows to be deleted, but retain Sources as a record of the content

## Decision Outcome

TBD

<!-- This is an optional element. Feel free to remove. -->
### Consequences

* Good, because {positive consequence, e.g., improvement of one or more desired qualities, …}
* Bad, because {negative consequence, e.g., compromising one or more desired qualities, …}
* … <!-- numbers of consequences can vary -->

<!-- This is an optional element. Feel free to remove. -->
### Implementation

{Once the proposal has been implemented, add a link to the relevant PRs here}

<!-- This is an optional element. Feel free to remove. -->
## Pros and Cons of the Options

### Option 1: Assume DELETE requests will be mediated by other systems, accept all requests

One approach to handling deletions is to assume a user or operator cannot directly call `DELETE` on a Flow or Source.
Instead in a well-engineered solution, another system mediates requests to the store to apply access control and workflow rules, and potentially add additional features such as multiple stores or caching.
In practice this system could be an extension to the core TAMS API, running as part of the implementation.

One such rule imposed by this "other system" could be to choose whether to perform a delete operation.
For example, an operators choice to delete may be combined with rules around archival and compliance recording.
Once all of these rules are satisfied, the other system can issue a `DELETE` request to the TAMS API.

* Good, because it avoids adding additional complexity to the TAMS API itself
* Good, because it helps make the case for intelligent, software-defined workflows
* Good, because it still allows un-needed essence to be cleaned up
* Good, because it also allows the metadata (Source and Flow records) to be removed when they are no longer needed
* Bad, because a user with access to the TAMS API can bypass the rules and make deletions anyway
* Bad, it encourages incompatible off-spec extensions of the API

### Option 2: Add `is_deleted` flag on Sources and Flows

When deleting Flows and Sources an `is_deleted` flag could be set instead of actually removing the object.
Then the listing endpoints (e.g. `GET /flows`) omit those items where that flag is set, unless instructed otherwise by a query string parameter such as `show_deleted=true`.

* Good, because it allows auditing of content that used to exist, even if it has since been deleted
* Good, because this auditing cannot be bypassed without direct manipulation of the underlying implementation
* Neutral, because it slightly breaks the REST-ful expectation that a `DELETE` causes the object to be removed.
* Bad, because it leads to potentially unbounded growth of the metadata database (especially if FlowSegments are flagged instead of deleted as well).
  Although this could be mitigated by building in some expiry or cleanup process in an implementation.

### Option 2a: Also add `is_deleted` to FlowSegments

Building on Option 2, a flag could also be added to FlowSegments to indicate that they have been deleted, and that portion of the timeline cannot be written to again.
Alternatively a more general way could be provided to represent that part of the timeline cannot be written to (e.g. FlowSegments with a `null` object ID).
Writing to a portion of the timeline where content already exists (even if the essence has since been deleted) would break the immutable nature of a Flow.

* Good, because it enforces immutability of Flows by preventing further writes.
* Good, because it allows meaningfully empty space to be represented.
  For example a Flow may have a gap because the content will never exist (e.g. the camera was turned off overnight), rather than because it hasn't been ingested/processed yet.
* Neutral, because it slightly breaks the REST-ful expectation that a `DELETE` causes the object to be removed (more significantly than Option 2, since the object still appears in the listing)
* Bad, because it prevents "restore from backup" or "refill cache" type operations from using the TAMS API directly

### Option 3: Allow Flows to be deleted, but retain Sources as a record of the content

Given that Flows are a representation of a piece of content abstractly described by a Source, it may make sense to handle Flow and Source deletions separately.
For a Flow, the FlowSegments (and therefore the essence) can be deleted, as well as the Flow itself, indicating the store is no longer holding that particular rendition.
However a Source cannot be deleted, because the _concept_ of the content still exists, even if the essence does not, and it may still be possible to reconstruct a Flow for that Source, for example by performing a rendering process.

* Good, because it acknowledges content (Sources) never really disappear, but their representations can
* Good, because it still allows FlowSegments (and their attached essence) to be deleted to manage storage space
* Good, because it also avoids proliferation of Flow records, since they can be deleted
* Bad, because it encourages proliferation of Source records (although they are a small piece of metadata with no essence attached directly), which can never be removed from a TAMS instance
