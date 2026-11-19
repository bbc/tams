---
status: "proposed"
---
# Support for both C2PA Live Media methods

## Context and Problem Statement

C2PA defines two live media methods: [per-segment C2PA Manifest Boxes (Section 15.4)](https://spec.c2pa.org/specifications/specifications/2.5/specs/C2PA_Specification.html#using_c2pa_manifest_box) and [Verifiable Segment Info (VSI, Section 15.5)](https://spec.c2pa.org/specifications/specifications/2.5/specs/C2PA_Specification.html#verifiable_segment_info).
Both can be stored in TAMS, but have different tradeoffs.
This ADR records whether TAMS guidance should select one method or accommodate both.

## Considered Options

* Option 1: Support VSI only
* Option 2: Support per-segment manifests only
* Option 3: Support both methods

## Decision Outcome

Chosen option: Option 3: Support both methods, because TAMS is a media store, not the authority for choosing between C2PA mechanisms.
Neither method is universally preferable, and selecting one would impose a TAMS-specific restriction on otherwise valid C2PA workflows.
The choice belongs to C2PA and, while both remain available, to the organisations integrating them.

Wider industry implementations are exploring both methods.
Supporting both respects existing implementation investment and encourages continued experimentation without TAMS favouring one approach.
This accepts a risk of ecosystem fragmentation and duplicated implementation effort.

Support means documenting storage and retrieval of either method, not requiring every TAMS client to generate or validate both.
Clients must establish which method is in use and whether their validators support it.
If C2PA later settles on a single approach, we will update this ADR and the associated application note to reflect that decision.

### Implementation

[Application Note 0011](../appnotes/0011-c2pa.md#live-workflow) describes both mappings using existing TAMS Media Objects and init Object references.
Signing and validation remain client responsibilities; the store preserves the signed bytes without translating between methods.
No new core API fields are required by this decision.

## Pros and Cons of the Options

### Option 1: Support VSI only

A signed manifest authenticates session public keys, while each media segment carries a compact, session-key-signed hash and segment information in an `emsg` box.

* Good, because clients sign individual segments with session keys rather than creating a full signed claim for each segment. Avoids storing and retrieving a full C2PA manifest with every media Object.
* Good, because recommending one method gives industry implementations a common target for TAMS integration and testing.
* Bad, because validation requires the applicable manifest and public session keys; clients must handle key updates and validity checks.
* Bad, because TAMS guidance would not cover per-segment manifest implementations.

### Option 2: Support per-segment manifests only

Each media segment carries a full signed C2PA manifest with its hash and live segment assertion, including continuity information.

* Good, because each media Object carries its own manifest and claim signature, reducing generation and validation complexity.
* Good, because recommending one method gives industry implementations a common target for TAMS integration and testing.
* Bad, because full manifests add metadata to every stored and retrieved media Object, and clients must sign a full claim for each segment.
* Bad, because TAMS guidance would not cover VSI implementations.

### Option 3: Support both methods

Document both approaches without selecting a preferred method.

* Good, because TAMS guidance accommodates both C2PA methods without prescribing an industry choice.
* Good, because existing implementations of either method can use the same TAMS storage model without converting their signed media.
* Good, because it respects existing industry investment and allows experimentation with both methods.
* Bad, because industry experimentation, guidance and interoperability testing must account for two methods, potentially duplicating effort.
* Bad, because clients may support different methods, risking fragmentation and pressure to implement both; storing either method does not guarantee compatible validation.