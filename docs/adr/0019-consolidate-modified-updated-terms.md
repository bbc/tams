---
status: "proposed"
---
# Rename `modified_by` properties in Source and Flow schemas to `updated_by`

## Context and Problem Statement

Core schemas for Sources and Flows have a property named `modified_by`.
Other properties use the term "updated" rather than "modified".
Whilst these terms may be considered interchangeable in some contexts, using both in the same schema is inconsistent and creates a potential source of confusion.

## Considered Options

1. Change `modified_by` to `updated_by`
2. Change other properties using the term "updated" to use the term "modified"
3. Do nothing

## Decision Outcome

Chosen option: 3: Change `modified_by` to `updated_by`

...because `modified_by` is the most recently-added property, and the degree of change to the spec is marginally smaller than option 2.
While doing nothing is an option, it was felt that although the terms may be considered interchangeable, retaining both is a potential source of confusion.
Consequently this should be fixed sooner rather than later, while the level of disruption to implementers (and the number of implementers) is relatively low.

The term "updated" is more consistent with commonly-used database `CRUD` terminology, so is more intuitive for those familiar with that domain.
The inconsistency was introduced unintentionally, so there is no valid rationale for retaining the use of both terms, except the fact that this is a breaking change, so will require a major version bump.
The downside is that this will potentially cause some inconvenience to implementers of TAMS services or clients - sorry!
However, there are breaking changes that need to be made imminently to address other issues.

We will bundle these into a single release to minimise disruption.

<!-- This is an optional element. Feel free to remove. -->
### Implementation

Implemented in PR [#60](https://github.com/bbc/tams/pull/60).
