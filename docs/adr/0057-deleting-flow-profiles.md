---
status: "proposed"
---
# Deleting Flow Profiles

## Context and Problem Statement

[ADR0047](../adr/0047-flow-profiles.md) added Flow Profiles to TAMS, implemented in [PR #130](https://github.com/bbc/tams/pull/130).
[AppNote0020](../appnotes/0020-using-flow-profiles.md) describes how Profiles may be used in practice.
That change provided endpoints to create, list and read Profiles, and defined Profiles as immutable once created.
However it did not provide a way to delete a Profile, nor explain why one cannot be deleted.

This was raised in [issue #248](https://github.com/bbc/tams/issues/248).
Flows created from a Profile reference it through their `profile_id`, so removing a Profile that is in use would break the link between those Flows and the Profile.
This would break discovery of Flows by Profile, and any other system relying on the Profile to describe those Flows.
Even so, there are real world cases where removing a Profile is needed, such as a Profile created by mistake with incorrect parameters, or a test that creates a Profile as part of its test material and needs to clean up after itself.

Rejecting the deletion of a resource because other resources still depend on it is a new concept for the TAMS API.
However the companion [TADS API](https://github.com/bbc/tads/blob/main/api/TimeAddressableDataStore.yaml) already takes this approach, rejecting the deletion of a Payload Schema while any Track refers to it.

This ADR discusses the options for supporting the deletion of Flow Profiles.

## Considered Options

* Option 1: No change
* Option 2: Document that Profiles cannot be deleted
* Option 3: Allow Profiles to be deleted only when not in use
* Option 4: Allow Profiles to be deleted at any time, leaving existing Flows unchanged
* Option 5: Allow Profiles to be deleted at any time, removing the link from existing Flows

## Decision Outcome

Chosen option: "Option 3: Allow Profiles to be deleted only when not in use", because it supports removing unused Profiles while protecting the link between Flows and the Profiles they were created from, and it matches the existing behaviour for Payload Schemas in TADS.

A `DELETE` method will be added to `/service/profiles/{profileId}`.
A Profile is in use when any Flow in the store references it in its `profile_id`.
Service implementations must reject a request to delete a Profile that is in use with a 400 response.
To delete such a Profile, Clients must first delete the referencing Flows or remove their link to the Profile, as described in AppNote0020.

Deleting a Profile only affects that store.
As Profile IDs are globally unique, the ID of a deleted Profile must not be reused for a Profile with different parameters, although the same Profile may be created again with the same ID and identical parameters.

The existing rule that Profiles are immutable is unchanged, since deleting a Profile is not an update.

### Implementation

Implemented in [PR #TBC](https://github.com/bbc/tams/pulls)

## Pros and Cons of the Options

### Option 1: No change

This option would maintain the current position with no changes to the API specification, or Application Notes.

* Good, because no changes are required in the specification
* Bad, because Profiles created by mistake or for testing remain in the store indefinitely
* Bad, because Clients are left unclear whether Profiles can be deleted, and why not

### Option 2: Document that Profiles cannot be deleted

This option would see no changes to the API specification, but AppNote0020 would state that Profiles cannot be deleted and explain why.
Profiles would be treated in the same way as Flow and Source IDs, which always refer to the same thing even if a store no longer holds a copy.

* Good, because no changes are required in the specification
* Good, because a Profile ID always resolves within a store once created
* Bad, because Profiles created by mistake remain in the store and in Profile listings indefinitely
* Bad, because tests that create Profiles cannot clean up after themselves

### Option 3: Allow Profiles to be deleted only when not in use

This option would see a `DELETE` method added for Profiles.
Service implementations would reject the request if any Flow references the Profile.
Clients could find the referencing Flows using the existing `profile_id` query parameter on the `/flows` endpoint.

* Good, because unused Profiles created by mistake or for testing can be removed
* Good, because Flows never lose the link to their Profile
* Good, because it matches the existing behaviour for Payload Schemas in TADS
* Neutral, because non-breaking changes are required in the specification
* Neutral, because Service implementations must check for referencing Flows before deleting a Profile
* Bad, because removing a Profile that is in use requires the Client to deal with every referencing Flow first

### Option 4: Allow Profiles to be deleted at any time, leaving existing Flows unchanged

This option would see a `DELETE` method added for Profiles with no restriction.
Flows would keep their de-normalised technical metadata and their `profile_id`, which would then refer to a Profile that no longer exists in the store.

* Good, because it is the simplest to implement
* Good, because Flows keep their technical metadata
* Neutral, because non-breaking changes are required in the specification
* Bad, because Flows are left referencing a Profile that does not exist
* Bad, because Flows can no longer be compared against or described by their Profile
* Bad, because creating new Flows from the deleted Profile fails, which may break workflows unexpectedly

### Option 5: Allow Profiles to be deleted at any time, removing the link from existing Flows

As with Option 4, but Service implementations would also remove the `profile_id` from all Flows that reference the deleted Profile, in the same way as a Client removing the link.

* Good, because no Flow is left referencing a Profile that does not exist
* Good, because Flows keep their technical metadata
* Neutral, because non-breaking changes are required in the specification
* Bad, because a single request silently modifies potentially many Flows, including ones the Client may not have permission to modify, or that are marked read-only
* Bad, because those Flows are no longer found when searching by Profile, breaking workflows such as edit by reference
* Bad, because the request could be long running for Profiles used by many Flows
