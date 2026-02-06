---
status: proposed
---
# Role Naming Convention

## Context and Problem Statement

Each item in the collection of a multi-essence Source or Flow has a `role`, intended as a description of that item's purpose in the collection.
Roles are intended to be human-readable, however it is useful for clients and systems to make sense of them too.
It would be useful to have some recommendations about how to use roles.

One part of that recommendation should be the editorial purpose of an item: for example programme audio, audio description or commentary. Or main video, signed video or clean-feed without graphics.

## Decision Drivers

* Roles must be set when creating a multi-essence collection.
* When viewing a multi-essence Source or Flow, only the list of IDs collected and roles are available: getting formats and tags requires another query.
* Items in a collection serve a variety of different purposes, and it is useful to have some commonality.

## Considered Options

* Option 1a: Provide guidance on how the free-text field `role` should be used
* Option 1b: Replace `role` with a number of additional controlled fields
* Option 2a: Represent purpose of content using a list, as with tags
* Option 2b: Represent editorial purpose using DVB component descriptors
* Option 2c: Represent editorial purpose using roles from MPEG-DASH
* Option 2d: Represent editorial purpose based on descriptions in the MovieLabs Ontology for Media Creation

## Decision Outcome

Chosen option: Option 1a and Option 2a, because this allows `role` to be free-form and evolve over time, and avoids a breaking change to the specification or unduly constraining it.
While this prevents clients from being able to automatically determine the purpose of each item in a collection, in many cases the role merely serves to change what the user is shown and they are left to make the decisions.
In cases where it matters which elements of a collection are picked up (for example packaging content for distribution) the correct items should be identified by some more rigorous method anyway (for example creating a multi-essence Flow of just the items required).

### Implementation

{Once the proposal has been implemented, add a link to the relevant PRs here}

<!-- This is an optional element. Feel free to remove. -->
## Pros and Cons of the Options

### Option 1a: Provide guidance on how the free-text field `role` should be used

Write an Application Note suggesting a naming convention for the `role` field, and that clients may also choose to query the members of the collection and consider their labels/tags directly instead.

* Good, because it avoids a breaking change to the specification, instead only creating guidance
* Good, because it makes `role` open-ended, allowing space for future change and expansion
* Bad, because it does not constrain the use of `role`, and clients may have to rely on human intervention

### Option 1b: Replace `role` with a number of additional controlled fields

Change the specification to remove `role` and replace it with a more precise set of fields conveying the purpose of each element in the collection.

* Good, because it constrains and precisely describes what each item in a collection is for.
* Bad, because it requires a breaking change to the API, to provide a capability that can be achieved another way.
* Bad, because it requires work to fully specify all the possible purposes an item in a collection can fulfil.
* Bad, because it then constrains TAMS and requires a change as new purposes are identified.

### Option 2a: Represent purpose of content using a list, as with tags

When describing the editorial purpose of an item in a collection, draw from a list of suggested types in an Application Note.
Allow new types to be added as they come up, in a similar process to tags.

* Good, because it captures suggested names without constraining the purposes that a Flow or Source can be used for
* Bad, because the list is open-ended and uncontrolled, which may lead to content using a mix of names

### Option 2b: Represent editorial purpose using DVB component descriptors

DVB uses the `stream_content`, `stream_content_ext` and `component_type` fields in the `component_descriptor` to describe the type of a Service.
These are described in [ETSI EN 300 468 pp 60-70](https://www.etsi.org/deliver/etsi_en/300400_300499/300468/01.19.01_60/en_300468v011901p.pdf).
TAMS could use the same descriptors, or their names.

* Good, because it is part of an established standard
* Bad, because the component types are represented as hex bytes (for carriage in the SDT table) and would need human-readable names
* Bad, because many of the types also include technical characteristics of content, making them unsuitable for use in Sources
* Bad, because the list is focused on distribution, so cannot contain aspects such as clean-feed video

### Option 2c: Represent editorial purpose using MPEG-DASH roles

MPEG-DASH contains a role 

**TODO!**

### Option 2d: Represent editorial purpose based on descriptions in the MovieLabs Ontology for Media Creation
**TODO!**
