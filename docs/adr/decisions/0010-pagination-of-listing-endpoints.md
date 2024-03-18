---
status: "proposed"
---
# Add pagination to Flow/Source listing endpoints

## Context and Problem Statement

A busy TAMS instance could potentially contain a very large number of Flows, and there should be a way to paginate through the responses.
This should be similar to the existing approach used by the `/flows/<flowid>/segments` endpoint.

## Considered Options

* Option 1: Provide query string parameters for page size limit, and offset or page number
* Option 1a: As above, but use an opaque "next page" key

## Decision Outcome

Chosen option: Option 1a (query string parameters with opaque key), because it is agnostic to the underlying implementation, in particular allowing paging to be trivially implemented both for SQL databases and managed NoSQL services like AWS DynamoDB.

### Consequences

* This approach means an application cannot directly construct the URL of a given page, however it is assumed in most cases results will be iterated or a single item looked up directly by UUID, so that limitation is assumed not to cause an issue.

### Implementation

Implemented by <https://github.com/bbc/tams/pull/33>

## Pros and Cons of the Options

### Option 1: Provide query string parameters for page size limit, and an offset/page number

Provide a query string parameter on the `/flows` and `/sources` endpoints specifying the number of items to return per page (`limit`) and one indicating which page to return `offset` or `page_number`.
Return suitable headers to help clients retrieve the next page (the `Link` header with `rel=next`), along with the actual paging limit applied (which may be different to the `limit` parameter, if the requested size is too large) and the position in the result set.

* Good, because it allows implementations and clients to control the number of results returned.
* Good, because pagination can be applied to URLs directly (e.g. a user can directly jump to a specific page without manipulating HTTP headers).
* Good, because the URL of an arbitrary page can be trivially constructed.
* Good, because the next page can be extracted from the `Link` header, and clients can implement an iterator pattern across the entire result set.
* Bad, because it's not directly compatible with some managed NoSQL services, which need to supply a specific string to paginate subsequent queries without scanning the entire dataset.

### Option 1a: As Option 1, but use an opaque "next page" key

As Option 1, but specify an opaque `page` key which the implementation understands how to resolve to the next page, instead of `offset` and `page_number`.
Return a `Link` header with `rel=next` (and a URL with `page` set appropriately) that clients can use to retrieve the next page in the result set.

* Good, because it is compatible with both SQL databases and NoSQL services, by changing how the implementation returns the value for the next `page` parameter
* Good, because it allows implementations and clients to control the number of results returned.
* Good, because pagination can be applied to URLs directly (e.g. a user can directly jump to a specific page without manipulating HTTP headers).
* Good, because the next page can be extracted from the `Link` header, and clients can implement an iterator pattern across the entire result set.
* Bad, because the URL of an arbitrary page cannot be trivially constructed, only iterated from the start.
