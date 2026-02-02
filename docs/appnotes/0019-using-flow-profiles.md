# 0019: Using Flow Profiles

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

If the content to be referenced is only coming from a one source (potentially with multiple Flows), for example a simple clip, then it is relatively easy to clone the technical parameters of the existing Flows and then join the Segments to the new Flow.
However if the content for the new edit is derived from multiple Sources then there is a need to match the Flows from the different Sources based on the technical characteristics.
Currently the TAMS API does not provide an easy method to do this, so it is necessary to compare all the Flows in code to find the matches.
The more Sources involved in this process, the harder this becomes.

## TAMS Profiles within the API

The TAMS Profile model is split into a number of stages:

* An endpoint to list and describe the available Profiles supported by the store
* The ability to supply a Profile when creating a Flow and the de-normalisation of the technical details to maintain read compatibility with non-Profile based Flows
* The ability to query Flows for a given Profile to easily and quickly find the required media type

### Profiles endpoint

It is possible to create and view Profiles via the dedicated API calls under the TAMS service end point (/services/profiles).
These Profiles hold all the technical parameters required to create a Flow in a single location.
A system looking to ingest standardised content into TAMS would create content matching one or more Profiles as defined in the endpoint.

A Profile should be treated as immutable, so once created it cannot be updated.
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

## Multi-store working with Profiles

The UUID of a Profile is assumed to be globally unique.
This is the same model as for Flow, Source and Object ID's which should be preserved when replicating content.

For workflows where replication of the same content formats are happening on a regular basis then it is recommended that the same Profile is loaded into both stores using the same UUID.
This will mean than when Flows are replicated between the stores then the Profile identifier will continue to link to the metadata.

If the Profile does not exist within the destination store then the Profile ID should continue to be preserved.
This will continue to allow the matching of content within the store by Profile ID, plus the Profile can be added later and will link to the existing content.

For workflows including more than two organisations it is recommended that one organisation takes responsibility for owning and publishing the Profiles.
These Profiles can then be loaded into the destination stores.
The organisation could be a single company or could be an industry body.
