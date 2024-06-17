# 0007: Populating Source Metadata

## Abstract

Sources and Flows include metadata properties such as `label`, `description` and `tags` that describe what the entity is and provides links to the context that created and uses the entity.
Flows are representations of Sources and therefore Flows share or inherit some metadata from Sources.
This Application Note provides some guidance on what to consider when populating Source metadata from Flows.

## Content

A Flow is a representation of a Source, where the (required) `source_id` Flow property identifies the Source.
Creating a Flow in TAMS will result in a minimal Source that has `id` and `format` properties matching the Flow's `source_id` and `format` properties..
A Source and Flow both have `label`, `description` and `tags` properties that may contain metadata about the entity.
An application needs to consider whether a metadata value should be set in the Source, Flow or both.

The primary link between the Source and Flow entities are their identifiers, which is the `id` Flow and Source property, and the `source_id` Flow property that references the Source.
If the identifiers are not known then the metadata can be used to discover Sources and Flows by using the query parameters when listing Flows and Sources in the TAMS API.
E.g. a GET of `/sources?tag.location=pallmall` will return all Sources that were created at the given `location`.
A similar query of Flows, `/flows?tag.location=pallmall` will return all Flows that have that tag.
Ideally these two queries should return the same group of Sources and Flows.

Adding metadata to Sources may provide an easier way to discover Flows and it also promotes the view of content as Sources that group Flows.
Systems and applications can then use the Source as the primary media content entity, abstracting out the specific and possibly ephemeral Flow rendition that may be used in a particular exchange or process.

An application may decide to populate the Source metadata from the initial Flow.
The Flow is created in TAMS which then automatically creates a minimal Source with `id` and `format` properties from the Flow's `source_id` and `format` properties.
The application can decide to copy the Flow's `label`, `descriptions` and `tags` to the Source.
However, a direct copy may not always be appropriate because some metadata may be specific to the Flow.
E.g. a `tag` that identifies the Flow to be a low bit rate proxy rendition.

Creating more Flows for a Source may bring more metadata that an application needs to decide whether it should be copied to the Source.
If the metadata applies to all Flows and is not tied to a specific rendition then it should probably be added to the Source.
