# 0018: Using Flow Profiles

## Abstract

The TAMS API is deliberately agnostic to the format of the media which it is managing, to allow for future compatibility with new formats without needing to change the API specification.
This provides challenges for interoperability and workflows such as edit by reference where standard media formats are required across multiple sources.

This document describes how flow profiles can be used within the TAMS API to simplify workflows while maintaining the flexibility of the core API.

## Challenges

### House formats

Within a customer deployment of TAMS it is expected that there would be limited number of recommended formats for users to work in.
Typically this could include a target format for the high quality media and standardised formats for proxy media and images.
These formats are typically refered to as House formats and do not preclude the storing of other content within the store, however it is likely to be normalised at some point to the house format.

The use of house formats then makes workflows such as ingest, rendering new content after editing, generation of proxy content and edit by reference easier.
House formats define one or more common formats for all the systems to utilise.

### Edit by reference flow matching

For edit by reference workflows there is a need both to create new sources and flows for the new item and also combine the segments together to create the new edit.

If the content to be referenced is only coming from a one source (potentially with multiple flows), for example a simple clip, then it is relatively easy to clone the technical parameters of the existing flows and then join the segments to the new flow.
However if the content for the new edit is derived from multiple sources then there is a need to match the flows from the different sources based on the technical characteristics.
Currently the TAMS API does not provide an easy method to do this, so it is necessary to compare all the flows in code to find the matches.
The more sources involved in this process, the harder this becomes.

## TAMS Profiles within the API

The TAMS profile model is split into a number of stages:

* An end-point to list and describe the available profiles supported by the store
* The ability to supply a profile when creating a flow and the de-normalisation of the technical details at the point of creation
* The ability to query flows for a given profile to easily and quickly find the required media type

### Profiles endpoint

It is possible to create and view profiles via the dedicated API calls under the TAMS service end point (/services/profiles).
These profiles hold all the technical parameters required to create a flow in a single location.
A system looking to ingest standardised content into TAMS would create content matching one or more profiles as defined in the endpoint.

A profile should be treated as immutable, so once created it cannot be updated.
Updating a profile would cause mismatches with flows which have been already created using that profile and so breaks the model for profiles.
To update a profile a new one with a new ID should be created.

The profiles endpoint has been designed to provide extensibility of the metadata through the same tags model as for flows and sources.
This would enable implementations to store additional metadata such as encoding parameters alongside the TAMS profile metadata

### Creating a flow using a profile

When creating a flow the generating system has two options:

1. Specify all the technical characteristics of the flow including the wrapper, codec and essence parameters alongside the non-technical parameters such as label and description
2. Provide just the technical profile for the flow and non-technical parameters required

When using the second option on submission of the create flow request, the store will then read the metadata for a given profile and use this to populate the metadata for the flow.
This de-normalisation of the technical parameters means that on the read side the flows created via both mechanisms have the same technical parameters available.
Additionally if the decision is made to change a standard profile in the future then this does not affect the existing flows as the parameters have already been replicated and should remain unchanged to reflect the media actually being stored.

Flows that have been created from a profile will include the parameter indicating which profile they were created from.
This differentiates them from the flows that have been created with the technical characteristics directly.

### Query flows using a profile

The get flows endpoint has the ability to query for flows with a given profile.  
When combined with other query parameters such as source id then this means it is easy to start matching content formats.

For example on an edit by reference workflow it would be possible to read the profile endpoint for the recommended profiles that content should have.
This then simplifies the process of creating the required flows and sources for the new content item.
The edit process could then process each input source in turn read the available flows and match them to the destination flows using the profile tag easily.
If the source content has additional non standard flows then these could be ignored.

From a flow created from a profile, it is possible to query via both profile ID and also the individual parameter of the flow that have been inheritied from the profile.

## Multi-store working with profiles

The UUID of a profile is assumed to be globally unique.
This is the same model as for flow, source and object ID's which should be preserved when replicating content.

For workflows where replication of the same content formats are happening on a regular basis then it is recommended that the same profile is loaded into both stores using the same UUID.
This will mean than when flows are replicated between the stores then the profile identifier will continue to link to the metadata.

If the profile does not existing within the destination store then the profile ID should continue to be preserved.
This will continue to allow the matching of content within the store by profile ID, plus the profile can be added later and will link to the existing content.

For workflows including more than two orgnaisations it is recommended that one organisation takes responsibility for owning and publishing the profiles.
These profiles can then be loaded into the destination stores.
The organisation could be a single company or could be an industry body.
