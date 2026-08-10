---
status: "accepted"
---
# Support for selectable presigned storage PUT URLs

## Context and Problem Statement

TAMS allows Client's to select whether `get_urls` for Objects returned by the `/objects/<id>` and `/flows/<id>/segments` endpoints are pre-signed or not.
The `/flows/<id>/storage` endpoint does not have an equivalent feature for `put_url`s.
It states that Clients should include credentials if the provided URL is on the same origin as the API itself, akin to the same-origin mode in the [WhatWG Fetch Standard](https://fetch.spec.whatwg.org/#concept-request-credentials-mode).
In practice, many Service implementations return pre-signed URLs instead.

Furthermore, the available options for storage URL authentication can present issues for business with mature security architecture policies that may be incompatible.

This ADR presents options for rationalising our approach to storage URLs and supporting varied security architectures.

## Considered Options

* Option 1: Maintain the current approach
* Option 2: Add query parameter allowing Clients to select presigned/non-presigned PUT URLs
* Option 2a: Define a default when this parameter is unset
* Option 3: Add attribute to signal if returned URLs are presigned
* Option 4: Allow out-of-band credentials in some cases
* Option 5: Allow Service Implementations to solely use out-of-band credentials
* Option 6: Return a list of PUT URLs on the `/flows/<id>/storage` endpoint

## Decision Outcome

Chosen options 2, 3, and 4.
This provides improved alignment between storage PUT and GET URLs.
It explicitly signals which auth methods Clients should use with these URLs.
It provides improved flexibility in deployment security models.
It avoids potential security holes.

### Implementation

Implemented in [PR #222](https://github.com/bbc/tams/pull/222).

## Pros and Cons of the Options

### Option 1: Maintain the current approach

This option would see no changes made.

* Good, because it doesn't require any spec changes
* Bad, because it is inflexible in terms of authentication methods with PUT URLs
* Bad, because PUT and GET URL approaches differ
* Bad, because popular Service Implementations do not implement the specified auth method

### Option 2: Add query parameter allowing Clients to select presigned/non-presigned PUT URLs

This option would see a `presigned` query parameter added to the `/flows/<id>/storage` endpoint that is akin to that on the `/flows/<id>/segments` and `/objects/<id>` endpoints.
If Option 6 is not chosen, the `If omitted, both presigned and non-presigned URLs will be returned.` sentence will be omitted as it only makes sense where multiple URLs are returned for the same Object.

* Good, because it is flexible in terms of authentication methods with PUT URLs
* Good, because PUT and GET URL approaches will be aligned
* Good, because it supports the auth methods used by popular Service Implementations
* Neutral, because it requires a non-breaking API change

### Option 2a: Define a default when this parameter is unset

If Option 6 is not chosen, this Option would see a different default specified.
It neither this Option and Option 6 are chosen, Service Implementations would be allowed to choose their own default.

* Good, because it provides clear expectations to the Client on default behaviour
* Bad, because it may be a breaking change for some Service Implementations
* Bad, because the chosen default may be incompatible with some deployment's security architecture

### Option 3: Add attribute to signal if returned URLs are presigned

This option would see an attribute added to the Flow Storage schema to explicitly signal if a returned URL is presigned, akin to that on the `/flows/<id>/segments` and `/objects/<id>` endpoints.

* Good, because it explicitly signals if a URL is presigned or not
* Good, because PUT and GET URL approaches will be aligned
* Neutral, because it requires a non-breaking API change

### Option 4: Allow out-of-band credentials in some cases

The specification currently allows presigned, or `same-origin` auth approaches to storage GET URLs.
It does note currently define auth approaches for different origin endpoints where presigned is not used.
This option would explicitly allow implementations to use out-of-band credentials in such cases.

* Good, because it adds clarity to a currently undefined case
* Good, because it allows common cloud-specific methods such as AWS IAM credentials to be used
* Neutral, because it requires a non-breaking API change

### Option 5: Allow Service Implementations to solely use out-of-band credentials

This option would permit implementations to only use out-of-band credentials to be used for storage URLs.

* Bad, because this would result in all clients requiring to produce implementation specific auth integrations to integrate with Storage Implementations which take this approach
* Bad, because this would compromise interoperability

### Option 6: Return a list of PUT URLs on the `/flows/<id>/storage` endpoint

This option would see the `/flows/<id>/storage` endpoint return a list of PUT URLs for each Object, akin to the `/flows/<id>/segments` and `/objects/<id>` endpoints.

* Good, because PUT and GET URL approaches will be aligned
* Bad, because it would be a breaking change in a core part of the specification
* Bad, because using these multiple URLs for a given Object may result in undefined behaviour
* Bad, because having multiple URLs for a given Object may result in security holes
