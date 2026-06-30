---
status: "proposed"
---
# Host Organisation for TAMS

## Context and Problem Statement

[ADR0046](./0046-governance.md) considered options for the future governance of TAMS, and concluded that it should move to an organisation such as the Linux Foundation.
At that time a process was set out (described in [GOVERNANCE.md](https://github.com/bbc/tams/blob/2190650f824b86bc6e53320538427cf0446d34e0/GOVERNANCE.md#phase-1-setup-period-now)) to form a TSC, identify a suitable organisation and move TAMS under it.
This ADR documents possible organisations and the associated decision.

## Decision Drivers

The TSC [identified](https://github.com/bbc/tams/wiki/TSC-Meetings-2026#next-steps-on-governance) a number of aspects to consider when selecting an organisation:

- How does governance work for projects?
  What is involved?
- What is the underlying legal structure?
- What is the funding model?
  Is it a paid membership organisation?
  Can non-members be involved?
- Is there a stated IPR policy/position?
- If there is a community, where is it?
  Can we join?
- Are they being talked about/engaged by organisations we’re working with in the TAMS Community?
  Can we see any evidence of that happening?

## Considered Options

Several possible organisations were identified, from discussions and suggestions by the TSC, their colleagues and others at the meetings.
Note that these options are in no particular order, except as to make the rest of the document flow better.

- Option 1: Linux Foundation (LF)
- Option 2: Academy Software Foundation (ASWF)
- Option 3: Cloud Native Computing Foundation (CNCF)
- Option 4: Joint Development Foundation (JDF)
- Option 5: Alliance for Open Media (AOM)

These options are all related, as illustrated by the following diagram (where boxes are organisations, and hexagons are example projects):
![Relationship between the organisations under the Linux Foundation umbrella](../images/ADRXXXX-LinuxFoundationFamilyTree.drawio.png)

## Decision Outcome

Chosen option: **TBD**, because

Option 5 (AOM) is unlikely to be a good fit based on the heavy focus on AV1, which TAMS is related to, but not closely.
Similarly Option 3 (CNCF) seems to consider projects which exist at another layer of the stack to TAMS.

{Justification, e.g., only option which resolves requirements, or comes out best (see below)}.

### Implementation

{Once the proposal has been implemented, add a link to the relevant PRs here}

## Pros and Cons of the Options

Note that in keeping with the other TAMS ADRs, options are characterised as “Good”, “Bad” or “Neutral”.
For the avoidance of doubt, that should be read as “a good/bad fit for the TAMS project at this time” rather than a value judgement on the organisations in question, and the wording exists as a very simple way to express strengths and weaknesses.

### Option 1: Linux Foundation

Become a project directly under the Linux Foundation, like [Media eXchange Layer (MXL)](https://github.com/dmf-mxl/mxl/).

At a basic level, Linux Foundation projects are required to use an open source licence, have a documented charter that separates their technical governance from the business needs of the organisations involved and allows anyone to participate in the technical community, and transfer ownership of their assets (repositories, domains, etc.) to a neutral party.

In terms of that neutral party, Linux Foundation projects are a “series” of LF Projects, LLC, a “series limited liability company” under Delaware law.
This effectively allows each project to be a distinct legal entity under the parent organisation, with separate obligations, assets and liabilities, without the overhead of managing a large number of companies (_note that this is the author's layperson's understanding, and not a qualified legal opinion_).

If desirable, a Linux Foundation project can become "funded", starting a "directed fund" to raise revenue (through membership) and spend it as directed.

On Intellectual Property Rights (IPR), it seems to rely on Apache 2.0 and similar licences containing a patent grant and then [Developer Certificate of Origin (DCO)](https://wiki.linuxfoundation.org/dco) sign-off indicating you were able to licence that contribution under Apache 2.0.
There is some cross-LF activity to defend members from Non-practicing Entities (also known as "patent trolls") depending on membership tier.

Linux Foundation projects have considerable freedom to operate as they see fit and build a community where they’d like.
To set up a project requires the support of at least one Linux Foundation member (both the BBC and AWS are members) and five sponsoring organisations (although it isn’t clear what that means).

- Good, because it offers us considerable freedom in how to operate TAMS
- Good, because it allows our existing community and process to remain, only changing the underlying ownership
- Good, because it is the lightest-touch of the options
- Good, because it creates space for TAMS applications outside of the Media & Entertainment sector, where it may find broader adoption
- Neutral, because while it is not a direct fit for TAMS, the Linux Foundation overall is very broad
- Neutral, because there would be additional steps to operate as a funded project, however this is no different to the existing model
- Bad, because we have to form, grow and run our own community (rather than being participants in an existing one)

### Option 2: Academy Software Foundation (AWSF)

Join the Academy Software Foundation (ASWF) as a project, like [OpenTimelineIO](https://github.com/AcademySoftwareFoundation/OpenTimelineIO).

ASWF is a subsidiary of the Linux Foundation, and shares many of the same aspects, for example the legal structure and requirements around licences, participation and ownership.
Its [charter](https://cdn.platform.linuxfoundation.org/agreements/aswf.pdf) describes its scope as:

> open source or open specification projects supporting the motion picture industry

The Foundation itself reads this fairly broadly, listing among its [goals](https://www.aswf.io/about/) to "share resources across the motion picture and broader media industries", however in practice many of the projects and members are active in the animation and visual effects space.

It is a membership organisation (a "Directed Fund" of the Linux Foundation), applying the overall principle of separating technical governance from business direction, while providing a way to to collect funds and spend them to further its goals based on the direction of [member organisations](https://www.aswf.io/members/).
For example, the ASWF funds its use of Slack and has a Working Group managing (and where necessary funding) some [CI infrastructure](https://www.aswf.io/ci-infrastructure/).

It also comes with more requirements in initial submission, including considering the potential "universe of participants" and presenting for approval to the [Technical Advisory Council (TAC)](https://tac.aswf.io/).
There is also a project lifecycle process into which projects are slotted: Sandbox, Incubation, Graduated, Archived.
Projects aim to move up from Sandbox to Incubation (or at least make demonstrable progress) within one year.
Moving to Incubation requires some more complete documentation and pass a growth assessment.
Annual Reviews take place to re-assess lifecycle stage and look over current activity, stage match and feedback.

### Slack and Community

One of our considerations is around what happens to the existing TAMS community, which is currently centred around a few core spaces (e.g. the CNAP Slack) and events (TAMSCon, the Community Call, etc.)

It seems the [ASWF Slack](https://slack.aswf.io/) is viewed as an enabler for the community it serves: providing a space for the groups involved to come together around a shared goal.
Members and participants have deep expertise is a wide variety of topics, and it serves the variety of projects under the ASWF umbrella well.
A few of the TSC members are also members of the ASWF Slack and can see the variety of technical discussions that take place, of a similar character to those in the CNAP Slack (however there are a number of useful private channels within the CNAP workspace: it is not clear to what extent this is possible in the ASWF community).

The ASWF Slack community is geared around a channel-per-project, e.g. there is a `#opentimelineio` channel, plus a handful of working group channels (e.g. `#opentimelineio-examples`).
In theory it is possible to merge workspaces together, exporting data from our existing workspace and then importing it to the new one, which would reduce (but not entirely mitigate) the impact of moving spaces.
One of the aspects the ASWF funds is a Slack Pro licence for their workspace, enabling retention of the message history beyond the 3-month limit of Slack Free.

### Events

Typically ASWF has a set of events that run across the Foundation: broadly the Open Source Forum, Open Source Days and Dev Days.
Of these the Open Source Forum and Open Source Days a in-person presentation sessions about software, open source and best practices (in Los Angeles) open to Foundation members, or members plus individuals for a registration fee.
Dev Days is a "hackathon" day where participants give a day of their time to work on a task from an Academy Software Foundation project.

In addition to this the various projects and Working Groups have their TSC and other meetings on a regular cadence, along with the fortnightly TAC meeting.

Currently the in-person events are in Los Angeles, although the Foundation have expressed that growing into Europe would have some appeal.

### Pros and Cons
- Good, because it is well aligned with the sector TAMS works in
- Good, because it provides a ready-made community to join an grow
- Good, because it provides a ready structure to manage funding and spending on resources
- Neutral/bad, because it is currently VFX/film focused (but seems keen to grow wider than that)
- Neutral/bad, because it introduces more process around managing the project
- Neutral/bad, because current events are all in the US (California) and the TAMS community is currently much more focused in Europe: many existing participants would be unable to attend in-person
- Bad, because it positions TAMS firmly within Media & Entertainment, when the technology may be more widely useful
- Bad, because it likely forces us to move our existing community, which may come at a cost of engagement and participation
- Bad, because we'd lose some of the freedom we enjoy to run and manage events within our community
- Bad, because very few of the existing TAMS community are Members of ASWF: in principle this isn't a barrier to technical participation, but limits event access

### Option 3: Cloud Native Computing Foundation (CNCF)

Join the Cloud Native Computing Foundation as a project, like [Helm](https://github.com/helm/helm).

CNCF is another subsidiary of the Linux Foundation, and shares many of the same aspects much like ASWF.
It is intended for projects that contribute to cloud-native ecosystem and provides a vendor-neutral home for open-source cloud-native projects.

Broadly a similar project lifecycle approach applies as with ASWF: there is an acceptance process for new projects, which then move through the stages.
On community, there are individual communities around projects (such as the Kubernetes community) but the broader cloud-native ecosystem means one community (e.g. a single Slack) is less likely to be practical.

- Bad, because most of the CNCF projects exist at a lower level that TAMS, providing underlying compute and platform capabilities to support a wide variety of applications, such as Kubernetes and Helm
- Bad, because we have to form, grow and run our own community (rather than being participants in an existing one)

### Option 4: Joint Development Foundation (JDF)

Form a Joint Development Foundation under the Linux Foundation, like the [Coalition for Content Provenance and Authenticity (C2PA)](https://github.com/c2pa-org).

JDF projects are a specific Linux Foundation structure intended for standards and specification projects, with a potential path to more formal standardisation.
JDF projects can also be funded or unfunded, and member organisations can be Steering Members, General Members and Contributor Members.
They are operated by a Steering Technical Committee (STC), which can run either "designated by consensus" (the model on which the TAMS TSC operates) or "designated by steering member", where Steering Member organisations provide a representative.
There’s also two operational modes: either “Community specification” (like TAMS, work is conducted asynchronously in public repos) with licences built for spec work, or “Traditional specification” as a more conventional specification process (C2PA is understood to use the latter).

JDF projects come with a more rigorous handling of IPR (especially in “Traditional” mode) requiring it to be considered explicitly, rather than the more general implicit grant in other projects through licences like Apache 2.0.

- Good, because it is intended for building specifications
- Good, because it has a more rigorous handling of IPR
- Neutral/bad because it is not aimed at building software directly, which increases friction should the TAMS community wish to own any software (e.g. store implementations).
- Bad, because the approach seems to differ somewhat from how TAMS is currently running as an open source project

### Option 5: Alliance for Open Media (AOM)

Become a project under the Alliance for Open Media, like [AV1](https://aomedia.org/specifications/av1/).

AOM is a JDF predominantly concerned with the developmnt and promotion of the AV1 codec.
While there is a working group considering [Storage and Transport Formats](https://aomedia.org/about/organization/#storage-and-transport-formats-working-group) the primary concern seems to be the codec itself.

- Bad, because of the significant focus on AV1
