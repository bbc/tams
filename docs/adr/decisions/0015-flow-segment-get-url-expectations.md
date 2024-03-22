---
status: "proposed"
---
# Make FlowSegment get_url expectations clearer

## Context and Problem Statement

Currently the API is not specific about how the segment `get_url` should work regarding credentials, and it is optional.
However in all current practical applications it is required as the only way for a client to retrieve actual media essence, and clients must understand the expectations placed upon them regarding credentials as well.

## Considered Options

Note that in this case, several of these options may be selected.

* Option 1: Make `get_url` mandatory in Flow Segments
* Option 2: Stipulate that requests to `get_url` should include same-origin credentials
* Option 3: Make `get_url` a list of `get_urls`

## Decision Outcome

Chosen option: Options 1, 2 and 3.
These changes make it more likely that clients will be interoperable, because they make shared assumptions about how those URLs work, and since clients are already using HTTP to access the API, it makes sense to use it for media objects as well.
Option 3 has a weaker justification, but in the absence of many implementations of TAMS (clients or servers) it makes sense to make it more flexible when the amount of change required to meet that flexibility is small.

### Consequences

* This is a breaking change to the API, and will trigger a major version increment
* However most existing client and store implementations already implement Options 1 and 2, so only the change to `get_urls` requires new code.

### Implementation

Implemented in <https://github.com/bbc/tams/pull/36>

## Pros and Cons of the Options

### Option 1: Make `get_url` mandatory in Flow Segments

Make the `get_url` property mandatory in the response to Flow Segment GET requests when using the "http_object_store" type (the only type currently described).
Similarly, make the `put_url` mandatory in the response to a request to the storage endpoint.

* Good, because it ensures clients are able to read and write media essence without needing additional protocols
* Good, because as a result it improves interoperability between client types
* Bad, because the spec will have to change to allow other backends, however relaxing restrictions in the spec is relatively easy to achieve

### Option 2: Stipulate that requests to `get_url` should include same-origin credentials

Stipulate in the description for `get_url` that clients should send the credentials used to access the API itself if the provided URL is on the same origin as the API endpoint (as understood by the [Same Origin Policy](https://developer.mozilla.org/en-US/docs/Web/Security/Same-origin_policy)) and otherwise should send no credentials.
As a result, for requests to different origins the API service should embed suitable credentials in the URL.
The spec should also indicate that clients should use consider the URLs they receive to be ephemeral, and to make a new request to the API in the case of a 403 Forbidden response, to avoid giving out long-lived URLs which could present a security risk.
This aligns with how pre-signed URLs in services like AWS S3 work.

* Good, because it allows flexibility in implementation to either access an endpoint hosted by the API server, or separate the metadata and data planes using managed cloud services.
* Good, because it aligns with the default behaviour in the [WhatWG Fetch Standard](https://fetch.spec.whatwg.org/#concept-request-credentials-mode) which sends credentials when the request is to the same origin.
* Good, because it allows implementations to apply security measures to the URLs they provide.

### Option 3: Make `get_url` a list of `get_urls`

Replace the `get_url` in a Flow Segment response with an array of `get_urls`, where a client can choose any of the items in that array.
Indicate that the list is sorted in order of the API server's preference - e.g. in the absence of any other reason clients should choose the first in the list.
Include a label alongside each `get_url` to describe its purpose.

* Good, because there are some use cases that would benefit from the `get_url` in a FlowSegment response being an array rather than a single value.
  For example a workflow could be implemented that accepts input from "A" and "B" contribution legs in a hitless switching arrangement, and proceeds to record both.
