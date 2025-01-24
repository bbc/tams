---
status: "proposed"
---
# Query Option to Filter get_urls

## Context and Problem Statement

Each Flow Segment returned by the `/flows/<flow id>/segment` endpoint includes a `get_urls` property that may include (labelled) URLs for fetching media objects.
The calculation of pre-signed URLs for example can result in an not insignificant increased request time.
Clients do not need the `get_urls` if they don't intend to fetch the media objects.
This ADR proposes adding a query option to filter the URLs that need to be included by a TAMS.

It was found that calculating a pre-signed URL for fetching a media object takes around 0.35 milliseconds when using the Python [boto3](https://github.com/boto/boto3) library.
That means a request to get 5000 Flow Segments will include around 1.75 seconds overhead to calculate the pre-signed URLs.
This was observed in a request to a TAMS which took around 4 seconds to return Flow Segments with pre-signed URLs and only around 2 seconds to return the same Flow Segments without pre-signed URLs.

The [boto3](https://github.com/boto/boto3) method to generate pre-signed URLs could also be optimised to reduce the time taken.
It was found that the older deprecated [boto](https://github.com/boto/boto) library took around 0.14 milliseconds to calculate a pre-signed URL, a 60% speed reduction when compared to [boto3](https://github.com/boto/boto3).
There are likely even more optimisations that could be made.

The pre-signed URL calculation may use a highly optimised implementation that avoids the large time overhead.
This would still result in larger response sizes because the pre-signed URLs tend to be quite large as they include signatures, keys and tokens.

It is difficult to predict what the expected number of flow segments will be in practice.
If it is low in all cases then including or not including pre-signed URLs doesn't make much difference.
If it is unknown then having an option to avoid the pre-signed calculation overhead may be useful in some cases.

## Considered Options

* Option 1: Always return all `get_urls`
* Option 2: Add a query option to return none or all `get_urls`
* Option 3: Add a simple query option to filter `get_urls` based on the `label`
* Option 4: Add more complex query option(s) to filter `get_urls`

## Decision Outcome

Chosen option: "Option 3: Add a simple query option to filter `get_urls` based on the `label`", because this covers the requirement to disable calculation of pre-signed URLs and at the same time allows other URLs to be retained.

### Implementation

Implemented in [PR #88](https://github.com/bbc/tams/pull/88).

## Pros and Cons of the Options

### Option 1: Always return all `get_urls`

This is the current state.

* Bad, because TAMS is doing work to calculate pre-signed URLs even though clients may not need them

### Option 2: Add a query option to return none or all `get_urls`

This adds a boolean option named `include_get_urls` that if set to `false` results in no `get_urls` in the response and therefore no pre-signed URLs are calculated by TAMS.

* Good, because it allows clients to indicate that `get_urls` are not required
* Bad, because some TAMS implementations may provide different types of URLs and a client does not have the option to filter out the ones that cause increased request time whilst retaining ones that don't

### Option 3: Add a simple query option to filter `get_urls` based on the `label`

This extends [Option 2](#option-2-add-a-query-option-to-return-none-or-all-get_urls) to add a (comma-separated) list option named `accept_get_urls` that specifies the `labels` associated with URLS to include in the response.
Omitting `accept_get_urls` will result in all URLs in the response.
Setting `accept_get_urls` to an empty string will result in no URLs in the response.
Flow segment `get_urls` with no label cannot be filtered.

* Good, because it allows clients to indicate that `get_urls` are not required
* Good, because clients can retain URLs that don't cause increased request times
* Neutral, because clients may want more complex filters based on what is available

### Option 4: Add more complex query option(s) to filter `get_urls`

This changes [Option 3](#option-3-add-a-simple-query-option-to-filter-get_urls-based-on-the-label) to allow more complex filtering based on what URLs are available.
E.g. include a URL for direct access to the object if available and otherwise a pre-signed URL.

* Good, because it allows clients to indicate that `get_urls` are not required
* Good, because clients can retain URLs that don't cause increased request times
* Neutral, because clients can use more complex filters based on what is available
* Neutral, because it isn't clear whether there is a requirement for more complex filters
* Neutral, because [0021](./0021-storage-label-format.md) thus far only proposes an App note for guidance on the use of `get_urls` labels on flow segments
