# 0020: Using Flow Profiles

## Abstract

The TAMS API is deliberately agnostic to the format of the media which it is managing, to allow for future compatibility with new formats without needing to change the API specification.
This provides challenges for interoperability and workflows such as edit by reference where standard media formats are required across multiple sources.

This document describes how Flow Profiles can be used within the TAMS API to simplify workflows while maintaining the flexibility of the core API.

## Challenges

### House formats

Within a customer deployment of TAMS it is expected that there would be limited number of recommended formats for users to work in.
Typically this could include a target format for the high quality media and standardised formats for proxy media and images.
These formats are typically referred to as House formats and do not preclude the storing of other content within the store, however it is likely to be normalised at some point to the house format.

The use of house formats then makes workflows such as ingest, rendering new content after editing, generation of proxy content and edit by reference easier.
House formats define one or more common formats for all the systems to utilise.

### Edit by reference flow matching

For edit by reference workflows there is a need both to create new Sources and Flows for the new item and also combine the segments together to create the new edit.

If the content to be referenced is only coming from a one source (potentially with multiple Flows), for example a simple clip, then it is relatively straightforward to clone the technical parameters of the existing Flows and then join the Segments to the new Flow.
However if the content for the new edit is derived from multiple Sources then there is a need to match the Flows from the different Sources based on the technical characteristics.
Currently the TAMS API does not provide an easy method to do this, so it is necessary to compare all the Flows in code to find the matches.
As more Sources are involved in this process then the matching process becomes more complex.

## TAMS Profiles within the API

The TAMS Profile model is split into a number of stages:

* An endpoint to list and describe the available Profiles supported by the store
* The ability to supply a Profile when creating a Flow and the de-normalisation of the technical details to maintain read compatibility with non-Profile based Flows
* The ability to query Flows for a given Profile to easily and quickly find the required media type

### Profiles endpoint

It is possible to create and view Profiles via the dedicated API calls under the TAMS service end point (/services/profiles).
These Profiles hold all the technical parameters required to create a Flow in a single location.
A system looking to ingest standardised content into TAMS would create content matching one or more Profiles as defined in the endpoint.

A Profile is treated as immutable - once created it cannot be updated.
Updating a Profile would cause mismatches with Flows which have been already created using that Profile and so breaks the model for Profiles.
To update a Profile a new one with a new ID should be created.

The Profiles endpoint has been designed to provide extensibility of the metadata through the same tags model as for Flows and Sources.
This would enable implementations to store additional metadata such as encoding parameters alongside the TAMS Profile metadata

### Creating a Flow using a Profile

When creating a Flow the generating system has two options:

1. Specify all the technical characteristics of the Flow including the wrapper, codec and essence parameters alongside the non-technical parameters such as label and description
2. Provide just the technical Profile for the Flow and non-technical parameters required

When using the second option on submission of the create Flow request it is simpler for the creating system.
The store is responsible for the de-normalisation of the technical parameters so that when reading from the API the Flows created via both mechanisms have the same technical parameters available.

Flows that have been created from a Profile will include the parameter indicating which Profile they were created from.
This differentiates them from the Flows that have been created with the technical characteristics directly.

### Query Flows using a Profile

The get Flows endpoint has the ability to query for Flows with a given Profile.  
When combined with other query parameters such as Source id then this means it is easy to start matching content formats.

For example on an edit by reference workflow it would be possible to read the Profile endpoint for the recommended profiles that content should have.
This then simplifies the process of creating the required Flows and Sources for the new content item.
The edit process could then process each input source in turn read the available Flows and match them to the destination Flows using the Profile tag easily.
If the Source content has additional non standard Flows then these could be ignored.

By the nature of the TAMS API it is possible to query via both Profile ID and also the individual parameters of the Flow that have been inherited from the profile.
As per standard behaviour, the API should only return results which match all fields, so for this scenario the Flow must have a profile ID and match the other parameters requested.

In future it is proposed to add additional match methods when querying Flows using a Profile.
This would include options for a "greedy match" where all Flows which match the technical characteristics are returned even if not created or updated to include a Profile.

### Updating Flows created using a Profile

For Flows created by specifying all technical characteristics directly, updates can include any of those parameters without restriction. 
When a Flow is created from a Profile then it inherits all the technical characteristics from the Profile.
This means if that Flow then needs to be updated then consideration needs to be given to the fields which were inherited.

For the standard fields (eg label, description, tags) which form part of the common Flow metadata and provided directly regardless of the Profile then these can be updated through the standard process.
For the fields inherited from the Profile then the store should reject an attempt to update them directly as a 400 error since this is a bad request.
The store should also provide a suitable error message indicating why it has rejected the update.

In the scenario where the technical characteristics do need to be changed on a Flow created from a Profile then it is necessary to remove the link to the Profile as part of the update since it will no longer match the Profile entirely.
This is achieved by means of sending the `profile_id` field with an empty string as part of the update.
This will then break the link to the Profile and allow the store to update the technical parameters.
It should be noted that searching for Flows using a Profile will no longer include the updated Flow since it no longer matches or is linked to the Profile.

## Multi-store working with Profiles

The UUID of a Profile is assumed to be globally unique.
This is the same model as for Flow, Source and Object ID's which should be preserved when replicating content.

For workflows where replication of the same content formats are happening on a regular basis then it is recommended that the same Profile is loaded into both stores using the same UUID.
This will mean than when Flows are replicated between the stores then the Profile identifier will continue to link to the metadata.

If the Profile does not exist within the destination store then it is not possible to create a Flow using the Profile and doing so should result in an error from the API that the profile does not exist.
The calling system then has two options:

1. Read the Profile from the originating store and create it using the same ID and parameters in the destination store.
It is important than no parameters of the Profile are changed in this operation otherwise this invalidates the principal of the Profile ID being the same across stores.
Once the Profile has been created successfully it should then be possible to re-try the Flow creation using the Profile ID.

2. The replication service could drop back to creating the Flow using the full metadata model without the Profile ID.
It could be possible to preserve the Profile ID through the use of a tag.

Option 1 is the preferred option and the correct way to handle profiles between stores and ensures the Profile ID is persisted between stores.
Option 2 should only be used if replicating content from a newer store that supports Profiles to an older store which does not.

For workflows including more than two organisations it is recommended that one organisation takes responsibility for owning and publishing a given Profile.
These Profiles can then be created in both the source and destination stores using the same UUID.
The organisation could be a single company or could be an industry body.

## Profile Impact on Bitrate Properties

The Profiles process splits the two bitrate fields `avg_bit_rate` and `max_bit_rate` such that they come from different places.
The `avg_bit_rate` is provided as part of the Profile, while the `max_bit_rate` remains part of the main flow metadata.

For the Profiles to work it is necessary for there to be a bitrate present in a Profile to be able to determine between different qualities where all the other technical parameters remain the same.
For example a h.264 file at 1080p50 could be at either 50Mbps or 100Mbps and this needs to be part of the Profile to be able to tell them apart.
This is why the `avg_bit_rate` is included in the Profile to enable this workflow.

In the context of Profiles the `avg_bit_rate` is considered to be the bitrate that the encoder is aiming to set for typical content.
This is not intended to take into account any unusually low bitrates which an encoder may create for static content such as bars or black.
Clients should not retrospectively update `avg_bit_rate` on a Flow that was created from a Profile, as changing the value would break the matching between the Flow and its Profile.

The `max_bit_rate` is defined in [AppNote 0013](https://github.com/bbc/tams/blob/main/docs/appnotes/0013-setting-flow-bit-rate-properties.md) and is considered the actual measured peak value of the segments in TAMS.
Since this is dependent on the actual behaviours of the encoder in relation to the actual content that is being encoded then this cannot be predicted in advance or will be consistent across Flows.
As such this cannot be included within a Profile and should be set by the encoder in the same manner regardless of whether the Flow was created directly or using a Profile. 