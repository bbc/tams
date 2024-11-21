---
status: "proposed"
---
# Flow Property Updates

## Context and Problem Statement

A Flow can be updated by PUTing the complete Flow, replacing it if it exists, or partially updated by PUTing or DELETEing some properties individually.
A Source can also be partially updated by PUTing or DELETEing some properties individually.

A Flow PUT requires all properties to be included, either set or unset.
This can cause some practical issues because TAMS clients could have a stale or incomplete copy of the Flow, particularly for those properties the client is not interested in or not intending to update.

The TAMS API already limits Source updates to those properties that can be updated.
A decision needs to be made on whether to prevent certain Flow properties from being updated.

Flow properties can broadly be categorised as follows:

* Properties that cannot be updated
  * The TAMS API prevents these properties from being updated
  * Properties:
    * `id`
      * The Flow `id` in the PUT data must match the ID in the endpoint path.
            This prevents it from being set to a different value.
* Properties that should be set once on creation and not updated.
  * Properties:
    * `source_id`
      * According to NMOS MS-04, a Flow is a representation of a single Source and therefore the `source_id` shouldn't change.
    * `generation`
    * `created_by`
      * Set by TAMS using request metadata, e.g. HTTP headers.
    * `format`
    * `codec`
    * `container`
      * A Flow could gain or lose media objects in TAMS, in which case this property can switch between being set and unset.
            A set value should however not be changed to another set value.
    * `container_mapping`
    * `description`
      * Some TAMS applications may require descriptions to be set at creation time.
    * `label`
      * Some TAMS applications may require labels to be set at creation time.
    * `max_bit_rate`
      * Some TAMS ingesters may calculate this over time and therefore it could be updated often.
            Ideally this information is known at Flow creation so that Flow readers can decide on the required receiver buffer sizes for example.
    * `avg_bit_rate`
      * This could be calculated on-the-fly.
            Ideally this information is known at Flow creation so that Flow readers know what data rate to expect.
    * Video:
      * `frame_rate`
      * `frame_width`
      * `frame_height`
      * `bit_depth`
      * `component_type`
      * `unc_type`
      * `horiz_chroma_subs`
      * `vert_chroma_subs`
    * Audio:
      * `sample_rate`
      * `channels`
      * `bit_depth`
      * `coded_frame_size`
      * `unc_type`
    * Data
      * `data_type`
* Properties that are set when they are known and then not updated.
  * These properties may not be known until further container and essence analysis, but once set should not be updated.
    If the properties are known then they should be set at Flow creation.
  * Properties:
    * Video:
      * `aspect_ratio`
      * `pixel_aspect_ratio`
      * `interlace_mode`
      * `colorspace`
      * `transfer_char`
      * `avc_profile`
      * `avc_level`
      * `avc_flags`
    * Audio:
      * `mp4_oti`
* Properties that can be updated
  * Properties:
    * `description`
      * Some TAMS applications may require descriptions to be set at creation time.
    * `label`
      * Some TAMS applications may require labels to be set at creation time.
    * `updated_by`
      * Set by TAMS using request metadata, e.g. HTTP headers.
    * `tags`
      * Some TAMS applications may require certain tags to be set at creation time.
    * `read_only`
    * `max_bit_rate`
      * Some TAMS ingesters may calculate this over time and therefore it could be updated often.
            Ideally this information is known at Flow creation so that Flow readers can decide on the required receiver buffer sizes for example.
    * `avg_bit_rate`
      * This could be calculated on-the-fly.
            Ideally this information is known at Flow creation so that Flow readers know what data rate to expect.
    * `flow_collection`
      * The list of elements can be changed but not the elements themselves.
* Properties that are set by TAMS and are read-only.
  * Properties:
    * `created`
    * `metadata_updated`
    * `segments_updated`
    * `collected_by`
    * `timerange`

A Flow is deemed to be complete if all the properties that define the static characteristics for the Flow are set.
This allows a TAMS API client to make decisions based on the information that is provided.

A Flow could have incomplete or incorrect information.
This means that the TAMS API should allow updates to properties that are normally expected to not change.
The Flow metadata may be incomplete on creation but could be completed before the Flow is used.

There could be systems that sit in front of the TAMS API that add restrictions to what can be updated.
A system could for example require a client to have the "created_by permissions" for the Flow to enable updates to the `description` and `label` properties.

## Considered Options

* Option a1: Prevent updates of properties that should not change
* Option a2: Continue to allow all properties to be updated with some exceptions

* Option b1: Add endpoints for all properties that can be updated
* Option b2: Add an endpoint with a path template matching the property that can be updated
* Option b3: Continue to use the current Flow PUT and property updates

* Option c1.1: Add a `/set` endpoint for PUTing to an arbitrary group of properties
* Option c1.2: Also add a `/unset` endpoint for PUTing to remove an arbitrary group of properties
* Option c2: Allow a PATCH update of a Flow
* Option c3: Add endpoints for PUTing to defined groups of properties
* Option c4: Continue to use the current Flow PUT and property updates

## Decision Outcome

The chosen options are: a2, b3 and c4.

Option a2 is chosen to allow all properties (with some exceptions) to be corrected and not require a Flow to be complete on creation.
It is expected that systems that sit in front of the TAMS API apply additional constraints on updates for a particular installation.
Clients SHOULD NOT update properties in the "Properties that should be set once on creation and not updated" category listed in the [Context and Problem Statement](#context-and-problem-statement) section, however TAMS implementations MAY permit it to correct mistakes and simplify client implementations.

Options b3 and c4 are chosen to keep the API simple at this stage until requirements for partial updates to Flows are clearer.

Option c3 looks the most promising if requirements emerge for updating groups of properties.

The API specification is changed (see [Implementation](#implementation)) to add endpoints to update `max_bit_rate`, `avg_bit_rate` and `flow_collection`.
This is done for consistency with other properties that have similar update characteristics.

### Implementation

Implemented endpoints for updating `max_bit_rate`, `avg_bit_rate` and `flow_collection` in [https://github.com/bbc/tams/pull/91](https://github.com/bbc/tams/pull/91).

## Pros and Cons of the Options

### Option a1: Prevent updates of properties that should not change

This option requires the Flow to be complete on creation such that all properties that should not change have been set.

* Good, because it ensures Flows are always complete and unchanged
* Bad, because it doesn't allow mistakes to be corrected
* Bad, because it assumes all information is available when initially creating a Flow

### Option a2: Continue to allow all properties to be updated with some exceptions

This is the current state.

* Good, because it allows mistakes to be corrected
* Neutral, because Flows may not always be complete when first created.
Applications would need to ensure that clients don't use a Flow that still needs to be completed.
* Neutral, because it relies on systems that sit in front of the TAMS API to apply additional restrictions

### Option b1: Add endpoints for all properties that can be updated

This option adds endpoints (and HEAD, GET, PUT and DELETE) for all properties that can be updated.

* Good, because it allows singular properties to be updated
* Bad, because it adds endpoints to the API that are unlikely to be used for properties that are expected to remain unchanged.
* Bad, because it increases the chance of race conditions when updating related properties

### Option b2: Add an endpoint with a path template matching the property that can be updated

This extends [option b1](#option-b1-add-endpoints-for-all-properties-that-can-be-updated) to use a path template for the property.
The path template is used to provides generic HEAD, GET, PUT and DELETE methods.
The path template parameter may restrict the list of properties.
A concrete path in the specification [overrides](https://swagger.io/specification/#paths-object) a path template.

* Good, because it makes it easier to specify endpoints and methods for singular properties
* Neutral, because a TAMS implementation and possibly the specification will likely still need to treat properties separately to avoid complexities surrounding additional validations, data types, etc.

### Option b3: Continue to use the current Flow PUT and property updates

This is the current state.

* Good, because it keeps the API stable and simple
* Neutral, because properties that are not expected to change are likely to be set or updated together at flow creation
* Neutral, because if properties need to be updated individually more often than was expected then an API extension should be made
* Bad, because the client needs to perform a GET prior to the PUT to mitigate differences between the local and remote Flow copies
* Bad, because the client needs to retain a full copy of the Flow to allow it to PUT an update to a smaller subset of properties

### Option c1.1: Add a `/set` endpoint for PUTing to an arbitrary group of properties

The `/set` endpoint can be viewed as a partial PUT on the Flow, supporting property setting for an arbitrary group of properties.

* Good, because it is simpler for clients to update the parts of the Flow that is of interest without needing to GET the Flow first
* Neutral, because it requires more work from the TAMS API to merge the changes with the current Flow.
However, that is already the case for endpoints for updating singular properties.
* Neutral, because having the `/set` endpoint adds a some extra complexity to the API
* Bad, because it doesn't support unsetting properties

### Option c1.2: Also add a `/unset` endpoint for PUTing to remove an arbitrary group of properties

This extends [c1.1](#option-c11-add-a-set-endpoint-for-puting-to-an-arbitrary-group-of-properties) to support deleting / unsetting properties.

* Bad, because having an `/unset` endpoint is not common practice

### Option c2: Allow a PATCH update of a Flow

A Flow PATCH method would allow partial updates to the Flow.

* Good, because it allows a partial update of a Flow
* Neutral, because it diverts from the current basic approach of only using GET, PUT, POST and DELETE methods
* Bad, because it adds some complexity to the API specification and implementation

### Option c3: Add endpoints for PUTing to defined groups of properties

This option takes the view that a client of the TAMS API wishes to update properties that relate to a particular aspect of or operation on a Flow.

The property groups could relate to an aspect of the Flow:

* essence properties
* segmentation and container properties
* descriptive properties
* Source and Flow relationships
* bit rate properties

The property groups could relate to a Flow operation:

* creation
* status updates
* grouping and relationships

A PUT to the group of properties is treated in the same way as a PUT to a Flow; a property is set if it is present and unset if not.

* Good, because it is simpler for clients to update the parts of the Flow that is of interest without needing to worry about the other parts of the Flow
* Good, because it supports both setting and unsetting
* Neutral, because a client will still need to do a GET (on the group) first to ensure it has the latest information
* Neutral, because it isn't clear whether there is a requirement for updating property groups

### Option c4: Continue to use the current Flow PUT and singular property updates

This option is equivalent to option [b3](#option-b3-continue-to-use-the-current-flow-put-and-property-updates).
