---
status: "accepted"
---
# Use Markdown ADRs to record design decisions

## Context and Problem Statement

For various reasons there is a need for transparency and clarity about the rationale for changes made to the TAMS API.
This is an open API definition that we hope will become widely adopted, so it is important that potential users can see how and why design decisions were taken.
It's also beneficial to anyone involved in the collaborative development of the API to have a historical record of design decisions, rationale and attribution for those decisions.

## Decision Drivers

* Need to track design decisions, rationales and attribution.
* Need to ensure development of the API is open and transparent
* Need to build in collaborative workflows to arrive at design decisions, that leave an audit trail

## Considered Options

* Use Github Issues
* Use Github Discussions
* Use [(M)ADR documents](https://adr.github.io/madr/), one per decision, version controlled using GitHub
* Use a combination of the above

## Decision Outcome

Chosen option: "Use (M)ADR documents, one per decision", because
Meets all of the requirements.
Could be supplemented with use of Issues and/or Discussions if/when the need arises, but these serve slightly different purposes.

### Consequences

* Good, because provides a mechanism for tracking design decisions from the start
* Good, because centralises the storage of these records alongside the API definition itself
* Good, because supports collaborative working in the open

### Implementation

Implemented by <https://github.com/bbc/tams/pull/15/>

## Pros and Cons of the Alternative Options

### Use GitHub Issues

It was felt that GitHub Issues exists to solve the problem of tracking problems rather than solutions

### Use GitHub Discussions

It was felt that GitHub Discussions, whilst a potentially useful adjunct to ADRs, doesn't really provide a structured, easy to parse way to document design decisions that makes implicit assumptions explicit

### Use some combination of the considered options

This will be kept under review, and other mechanisms may be introduced to support the use of ADRs
