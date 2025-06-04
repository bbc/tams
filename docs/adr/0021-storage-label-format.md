---
status: "superseded by ADR-0032"
---

# Label Conventions for get_urls

## Context and Problem Statement

At an in-person discussion session in May 2024, there was discussion around putting together some guidance on the use of `get_urls` labels on flow segments.
This would provide information to aid the selection of URLs where multiple are available.
This ADR explores options for where to specify a means to signal this information.

## Considered Options

* Specify a schema against the `get_urls` label parameter of Segments within the API specification
* Specify a schema in an application note
* Make no specifications/recommendations

## Decision Outcome

Chosen option: "Specify a schema in an application note", because while specifying a consistent approach will provide significant benefit, any approach will need proving in the real world before making a core part of the specification.

### Implementation

Application note 0009 included in [PR #72](https://github.com/bbc/tams/pull/72).

## Pros and Cons of the Options

### Specify a schema against the `get_urls` label parameter of Segments within the API specification

* Good, because implementers can rely on the format of the information
* Good, because implementers are provided enough information to make informed decisions on which URL to use
* Bad, because it will be a breaking change to the API
* Bad, because the approach hasn't been validated in real world implementations and may need to be modified in future

### Specify a schema in an application note

* Good, because implementers are provided enough information to make informed decisions on which URL to use
* Good, because it is not a change to the API itself
* Good, because it allows the approach to be validated in real world implementations
* Bad, because implementers cannot initially assume others will be using the specified format

### Make no specifications/recommendations

* Good, because it is not a change to the API or its use
* Bad, because implementers cannot make informed decisions on which URLs to use beyond matching specific labels

## More Information

The need for this ADR was identified at the first CNAP in-person event on the 9th-10th May 2024.

This approach should be re-visited once it has been validated in real-world implementations to consider moving this functionality into the core specification, and whether that should be done as seperate JSON parameters as opposed to a formatted string.
