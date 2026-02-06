# Principles

These principles describe both what TAMS is (and isn’t) as a technology, and also some of the principles that define it’s direction and development.
The TSC use these to guide technical decision making and shape the direction of the project.

## What is TAMS?

Overall, TAMS and the TAMS API is an interface for writing media to and reading it from a store.
It provides a framework for sharing that media between systems, solutions and organisations using a content-centric, cloud-native approach, all focused around a store (or a number of stores).

1. TAMS is designed to be interoperable.
   Having TAMS support should enable integration with other TAMS solutions, removing or minimising the need for bespoke integrations.
2. TAMS is agnostic to clouds, codecs, and containers.
   It may describe how to integrate with a particular technology, but the core API can be implemented in many ways for many purposes.
3. TAMS is for media.
   While it also works for data (and has data as a supported type) it is primarily designed for media-like workflows on a timeline.
4. TAMS supports fast-turnaround/near-live workflows, but also works well for file-based workflows, and in some cases can take the place of live signal-centric workflows, if appropriate latency tradeoffs can be made.
5. TAMS does not implement a MAM.
   It should contain the minimum possible content discovery and library management features.
   Anything else should go in a system designed for that purpose.
6. TAMS is open source to reduce barriers to entry and maximise adoption: anyone should be able to participate in the ecosystem, providing maximum choice.
7. TAMS is a living specification.
   It will evolve over time to meet the needs of the community.
8. The TAMS repository contains the core specification and schemas, along with various examples to help implementers and Application Notes covering best practices and possible approaches to specific areas or technologies.

## Guiding Principles

1. TAMS is a small sharp tool.
   It does not solve all problems in all ways.
2. TAMS and the API should be as simple as possible, and always strike a balance across aspects such as complexity, capability, scalability.
3. TAMS API servers and clients with compatible versions should interoperate.
   The specification is prescriptive and opinionated where necessary to enable this.
4. However we aim to give users as much flexibility as possible while ensuring interoperability.
5. Optional features and capabilities are used cautiously, to simplify client implementations and reduce integration engineering work.
6. We re-use patterns and approaches where possible: both within TAMS, and drawing on existing approaches in other technologies.
7. Breaking changes are possible, but we strike a balance to minimise impact and maximise benefit.
   We make decisions with strong engineering justification and consider the impact of change, through an open decision process.
8. The TAMS community is governed by a balanced mix of users (broadcasters, content owners etc.) and technology/solution vendors.
