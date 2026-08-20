# Principles

These principles describe both what TAMS is (and isn’t) as a technology, and also some of the principles that define it’s direction and development.
The TSC use these to guide technical decision making and shape the direction of the project.

## What is TAMS?

Overall, TAMS and the TAMS API is an interface for writing media to and reading it from a store.
It provides a framework for sharing that media between systems, solutions and organisations using a content-centric, cloud-native approach, all focused around a store (or a number of stores).

1. TAMS is designed as an interoperable media framework.
   Having TAMS support should enable integration with other TAMS solutions, removing or minimising the need for bespoke integrations.
2. TAMS is agnostic to clouds, codecs, and containers and is intended to deploy anywhere, including on-premise and at the edge.
   It may describe how to integrate with a particular technology, but the core API can be implemented in many ways for many purposes.
3. TAMS is for media.
   It is primarily designed for media-like workflows on a timeline, however it also works for data-as-media that is accessed through the index of time (and as such, has data as a supported type).
4. TAMS supports fast-turnaround/near-live workflows, but also works well for file-based workflows, and in some cases can take the place of live signal-centric workflows, if appropriate latency tradeoffs can be made.
5. TAMS does not implement a MAM.
   It should contain the minimum possible content discovery and library management features required for effective interoperability.
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
5. The specification is agnostic to implementation, and we avoid implementation details driving decision-making (however we strike a balance in writing a specification that can be implemented)
6. Optional features and capabilities are used cautiously, to simplify client implementations and reduce integration engineering work.
7. We re-use patterns and approaches where possible: both within TAMS, and drawing on existing approaches in other technologies.
8. Breaking changes are possible, but we strike a balance to minimise impact and maximise benefit.
   We make decisions with strong engineering justification and consider the impact of change, through an open decision process.
9. The TAMS community is governed by a balanced mix of users (broadcasters, content owners etc.) and technology/solution vendors.
10. When common requirements arise, or the need for a common piece of functionality becomes clear, we attempt to standardise an approach either in the API Specification or an Application Note to enable interoperability.

## The Bigger Picture

TAMS is part of a bigger transformation of how media workflows, supply chains and the organisations that run them work in an increasingly software-defined world.
In the past, a conventional view of broadcast technology was to build a physical facility and deploy a technical estate that suited the organisation for a timeline measured in years.
This has already changed, with many organisations looking to the cloud for more flexibility, and accepting capable but monolithic solutions either managed in their own cloud infrastructure, or through a SaaS model.

However the needs of audiences and the shape of media and entertainment markets continue to shift, and shift very rapidly, demanding agility from the broadcasters, distributors and content creators that serve them.
To support that agility, media organisations want to take smaller components from the market that integrate well together on shared interoperable foundations.
They want to join components together around functional blocks and be free to experiment with new experiences and capabilities, deciding in each case whether to buy from the market, build themselves or assemble from smaller pieces.

TAMS solves one particularly troubling problem in this tranformation: sharing media between tools and systems, whether they are in the cloud, in a facility or in the field.
End-users can assemble powerful workflows out of those tools and systems, with confidence in interoperability through TAMS, and the agility to replace/upgrade or innovate as they see fit.

The need for open standards is well understood by the broadcast sector: many industry organisations have a long history of developing and managing standardisations efforts.
The challenge is the speed of change: TAMS has deliberately taken a "rough consensus and running code" approach ([borrowed from the IETF](https://www.ietf.org/runningcode/)), working as an iterative open source project that evolves fairly quickly but has strong versioning semantics to assure interoperability.
TAMS is not the only project on this journey, for example the [Media eXchange Layer (MXL)](https://github.com/dmf-mxl/mxl) takes the same open-source approach for low-latency live production under the [Dynamic Media Facility](https://www.amwa.tv/jtdmf) initiative.

As our market continues to shift and blur the traditional lines between broadcasters, content creators and distribution platforms, an open source approach and common foundations enables the technology to serve the needs of creative teams, rather than the other way around.
