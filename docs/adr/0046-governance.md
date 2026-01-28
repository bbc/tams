---
status: "accepted "
---
# Governance

## Context and Problem Statement

TAMS was open-sourced by BBC R&D in 2023, and since then the BBC has owned the repository and coordinated contributions.
While this made sense initially, it is part of BBC R&D’s remit to transform the broadcast industry by maturing and scaling our technology to be governed by the community, rather than for the community.
To that end, there needs to be a sustainable governance model for TAMS which invites broad participation from broadcasters, technology vendors and infrastructure providers and some way to ensure that TAMS will continue in the long term.

## Decision Drivers

* TAMS has grown in maturity, and a widening ecosystem of products is emerging around it
* More people and organisations are depending on TAMS, and relying on it being stable
* A formal governance process provides a framework to make decisions
* TAMS is of interest to a range of organisations, some of which are uncomfortable that the BBC has complete control
* An open ecosystem is advantageous to continued growth and success of TAMS, and benefits many areas of the media industry and adjacent verticals
* TAMS is an evolving software specification that iterates fairly rapidly in response to the needs of the community, and the approach taken should fit this model

## Decision Outcome

Chosen option: Option 2: Move to an organisation such as the Linux Foundation, because TAMS is ultimately a software specification, so a software oriented approach seems appropriate.
Furthermore such organisations offer lightweight governance and the freedom to move quickly, while fostering an open ecosystem.

<!-- This is an optional element. Feel free to remove. -->
### Implementation

{Once the proposal has been implemented, add a link to the relevant PRs here}

## Pros and Cons of the Options

Note that in keeping with the other TAMS ADRs, options are characterised as “Good”, “Bad” or “Neutral”.
For the avoidance of doubt, that should be read as “a bad fit for the TAMS project at this time” rather than a value judgement on the organisations in question, and exist to explore worst-case scenarios as well.

### Option 1: Keep TAMS under the control of the BBC

Retain the current position, where TAMS remains part of the BBC GitHub organisation and under overall control of the BBC.
BBC R&D continue to lead decisions and direction of the specification in the existing ad-hoc manner.

* Good, because it is the status quo and requires no change
* Bad, because technical direction and decisions are set by a single organisation ad-hoc
* Bad, because the community doesn’t own or control the roadmap
* Bad, because organising the community and associated tools have to operate within or around the BBC’s public-sector Fair Trading requirements
* Bad, because it creates complexities for some organisations depending on their relationship with the BBC
* Bad, because hypothetically the BBC could decide to stop working on the project or remove the repository

### Option 2: Move to an organisation such as the Linux Foundation

Become a project under an existing open-source software organisation such as the Linux Foundation, operated by a steering committee composed of members from various organisations, with a formal charter and decision making process.

* Good, because TAMS becomes owned by the community and driven by consensus
* Good, because there are many existing successful projects managed in the same way (e.g. MXL)
* Good, because these organisations are open: anyone can participate
* Good, because open governance aids longevity: even if the BBC stepped back, the project can continue
* Good, because these organisations are software-oriented, which matches well to the existing development practices for the TAMS API
* Neutral, because the Linux Foundation is not a media-specific organisation
* Neutral, because there is a risk of a “design-by-committee” approach slowing down decision making, which can be mitigated through an effective charter, TSC and set of decision principles

### Option 3: SMPTE Standardisation Process

Work through the process for TAMS to become a recognised SMPTE standard, with future changes managed through SMPTE processes.

* Good, because SMPTE standards are highly regarded within the broadcast industry
* Good, because SMPTE standards are very stable
* Bad, because the ability of the TAMS API to change and evolve as software would be significantly limited
* Bad, because the SMPTE standardisation process is heavyweight and takes a long time

### Option 4: AMWA and similar Industry Bodies

Move TAMS to be published and stewarded under an industry body such as AMWA, the DPP, or the EBU.

* Good, because those organisations are recognised for other specification work in the industry (such as AMWA NMOS, DPP AS-11 and EBU ADM)
* Neutral, because while AMWA et al are not entirely software-oriented, they have projects in the software domain that work well and have some expertise in that domain
* Bad, because participation can be limited to qualifying members of those bodies (in some cases imposing geographic restrictions)

### Option 5: Form a new Industry Organisation

Form a new organisation focused on the development and furthering of TAMS as a technology, collaborating with (but operating separately to) existing groups such as AMWA, VSF, EBU, DPP.
Set up a suitable group to govern and operate the new organisation, along with the relevant legal frameworks to allow it to exist on its own.

* Good, because it allows TAMS complete control over how it is governed and run
* Bad, because setting up and running a new organisation requires considerable work and overhead
* Bad, because more groups to work with creates more overhead in cross-industry activities
* Bad, because setting up and running the organisation would require some funding (e.g. for legal support), and it is not clear where this would come from
