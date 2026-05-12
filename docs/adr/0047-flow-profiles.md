---
status: "accepted"
---
# Adding Flow Profiles to TAMS

## Context and Problem Statement

The TAMS API is deliberately agnostic to the format of the media which it is managing.
This provides challenges for content discovery and interoperability in workflows such as edit by reference where standard media formats are required across multiple sources.

The aim of adding Profiles to TAMS is to centralise the common technical metadata across multiple Flows.
This means that it is easier to discover the required formats of the content (eg proxy) using the profile rather than needing to match multiple technical parameters.

The full details of how Profiles work has been documented in AppNote [#0020](https://github.com/bbc/tams/blob/main/docs/appnotes/0020-using-flow-profiles.md)

## Considered Options

Option 1: Add Flow Profiles to the core specification
Option 2: Add Flow Profiles with advanced search criteria
Option 3: Do nothing

## Decision Outcome

Chosen option: "Option 1: Add Flow Profiles to the core specification".
This is to allow the current scope of option 1 to be merged without being delayed due to a lack of clarity about all the possibilities for option 2.

It is expected that there will be a second PR/ADR to cover option 2 once the requirements have been clearly defined.

### Implementation

See the API specification changes in PR [#130](https://github.com/bbc/tams/pull/130).

## Pros and Cons of the Options

### Option 1: Add Flow Profiles to the core specification

A new API resource shall be added under /services/profiles to centralise the technical metadata (format, codec, container, essence parameters) for commonly used Flow configurations. 
The Flow creation endpoint shall accept a profile_id in place of individual technical parameters, with the store responsible for de-normalising the Profile metadata onto the Flow for read compatibility. 
The Flows listing endpoint shall gain a profile_id query parameter, enabling discovery of all Flows matching a given Profile across one or more Sources. 
Profiles shall be immutable once created; updates shall require creating a new Profile with a new UUID, and Profile IDs shall be preserved across stores during replication.

- Good: Centralising the technical metadata for Flows where it is the same
- Good: Simplifies content discovery (eg proxy version) to a single query parameter
- Good: Provides central place for referencing "house" formats for a store, with extensibility through tags to hold additional metadata (eg encoding parameters)
- Good: Backwards compatibility with all existing workflows retained
- Bad: Drives significant re-working of the API specification structures
- Bad: Does not currently support "greedy matching" (finding Flows that match a Profile's technical characteristics but were not explicitly created with that Profile)
- Bad: Multi-store coordination of Profile UUIDs requires out-of-band agreement between organisations
- Bad: The de-normalisation step adds implementation complexity on the server side

### Option 2: Add Flow Profiles with advanced search criteria

This option builds on Option 1 and adds an additional query parameter to define the Profile match mode on the Flows listing endpoint.
Options would include matching flows which share the technical characteristics as a Profile but have not been associated with it.
Alternatively it could be used as an exclude to look for all Flows which match a profile but have not been linked to it.

- Good: Enables brownfield adoption — existing Flows that match a Profile's technical characteristics become discoverable
- Good: Simplifies edit-by-reference workflows across mixed content where some Flows were created with Profiles and others were not
- Good: Makes Profiles useful as a query template even in stores where Profile-based creation has not been universally adopted
- Bad: Requires clear definition of what constitutes a "match"
- Bad: Full requirements and all possible match modes have not been fully defined

### Option 3: Do nothing

- Good: No changes to the API and implementations
- Bad: Remaining challenges around content discovery remain
- Bad: Edit-by-reference workflows continue to require client-side matching of all technical parameters across multiple Sources
- Bad: No formal mechanism for defining or communicating house formats between systems