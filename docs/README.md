# Supporting Documentation

## ADRs

This repository uses [(M)ADR documents](https://adr.github.io/madr/) to propose significant changes, facilitate discussions and decision making, and to store a record of options that were considered.
The following is an index of currently available ADRs.
For more information on how we use ADRs, see [here](./adr/README.md).

| ADR Number                                                         | Title                                                                      |
| ------------------------------------------------------------------ | -------------------------------------------------------------------------- |
| [0000](./adr/0000-use-markdown-adrs-to-record-design-decisions.md) | Use Markdown ADRs to record design decisions                               |
| [0001](./adr/0001-expand-created-modified-metadata.md)             | Expand Created-by and Modified-by Metadata                                 |
| [0002](./adr/0002-add-sources-to-api.md)                           | Add Sources as objects in the API                                          |
| [0003](./adr/0003-item-timestamps-managed-internally.md)           | Created and Modified Timestamps should be managed internally               |
| [0004](./adr/0004-content-deletion.md)                             | Deletion of Content and IDs                                                |
| [0004a](./adr/0004a-ancestry-relationships.md)*                    | Flow and Source References                                                 |
| [0005](./adr/0005-flow-read-write-permissions.md)                  | Flow Read-Write Permissions                                                |
| [0006](./adr/0006-flow-status.md)                                  | Flow Update Status                                                         |
| [0007](./adr/0007-use-timerange-in-flow-segments.md)               | Use Timerange in Flow Segments                                             |
| [0008](./adr/0008-move-flow-parameters-into-a-sub-property.md)     | Move Flow Parameters into a sub-property                                   |
| [0009](./adr/0009-allow-segment-overlap.md)                        | Allow Segments to Overlap                                                  |
| [0010](./adr/0010-pagination-of-listing-endpoints.md)              | Add pagination to Flow/Source listing endpoints                            |
| [0011](./adr/0011-random-storage-object-ids.md)                    | Random Storage Object IDs                                                  |
| [0012](./adr/0012-add-flow-collections.md)                         | Add collections to flow and source metadata schemas                        |
| [0013](./adr/0013-timeline-exposed-by-flows.md)                    | Timeline exposed by Flows                                                  |
| [0014](./adr/0014-add-event-stream.md)                             | Add an event stream to the TAMS API                                        |
| [0015](./adr/0015-flow-segment-get-url-expectations.md)            | Make FlowSegment get_url expectations clearer                              |
| [0016](./adr/0016-checksums-and-filesize.md)                       | Add Object Checksums and Filesizes                                         |
| [0017](./adr/0017-container-mapping.md)                            | Defining the Container Mapping to a Flow                                   |
| [0018](./adr/0018-restrict-direct-source-modification.md)          | Restrict direct Source modification                                        |
| [0019](./adr/0019-consolidate-modified-updated-terms.md)           | Rename `modified_by` properties in Source and Flow schemas to `updated_by` |
| [0020](./adr/0020-version-signalling.md)                           | Improving the signalling of the supported API version in implementations   |

\* Note: ADR 0004a was the unintended result of a number clash in the early development of TAMS which wasn't caught before publication

## Application Notes

Application notes are informatative documents describing the recommended usage of the API.
For more information on how we use application notes, see [here](./appnotes/README.md).

| Application Note Number                                          | Title                                                         |
| ---------------------------------------------------------------- | ------------------------------------------------------------- |
| [0001](./appnotes/0001-multi-mono-essence-flows-sources.md)      | Practical Application of the TAMS Content Model               |
| [0002](./appnotes/0002-Timing-in-MPEG-TS.md)                     | Timing in MPEG-TS                                             |
| [0003](./appnotes/0003-tag-names.md)                             | Tags, how to use them, and how we manage them                 |
| [0004](./appnotes/0004-tams-for-data.md)                         | When TAMS is a good fit for non-media data. And when it’s not |
| [0005](./appnotes/0005-indepentent-segments.md)                  | Media objects should be independently decodable. Here's why   |
| [0006](./appnotes/0006-containers-and-mappings.md)               | Containers and Mappings                                       |
| [0007](./appnotes/0007-populating-source-metadata.md)            | Populating Source Metadata                                    |
| [0008](./appnotes/0008-timestamps-in-TAMS.md)                    | Timestamps in TAMS                                            |
| [0009](./appnotes/0009-storage-label-format.md)                  | Storage label format specification                            |
| [0010](./appnotes/0010-long-running-sources-and-flows.md)        | Long-running Sources and Flows                                |
| [0010](./appnotes/0011-c2pa.md)        | C2PA provenance across related Sources and Flows |
