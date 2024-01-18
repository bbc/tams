# Decisions

This directory contains decision records for the TAMS API, describing the rationale behind decisions about the API, along with which other options were considered and the potential implications.
They exist to describe proposals, to facilitate discussions and decision making, and to serve as a concise record of those discussions.
The full list is located as Markdown files [in this directory](./).

These records are based on the Markdown Any Decision Record template - see <https://github.com/adr/madr> for the original template, and <https://adr.github.io/> for more on ADRs in general.

ADRs will be submitted using GitHub PRs, which provides necessary tooling for community review and approval.
Not all changes to the API definition will warrant an ADR.
One of the tests that will need to be applied on review of PRs containing ADR docs, and PRs that don't, is that of architectural significance.

## Creating a new ADR

0. Look at the existing list of ADRs, and see if this has been considered before, or whether it would supersede any of them
1. Copy the [adr-template.md](../template/adr-template.md) into this directory
2. Name it with the next number in sequence, and a sensible title (e.g. `00023-improve-source-hierarchy.md`)
3. Fill in the template: at least the "Context", "Considered Options" and "Pros and Cons..." sections.
   Feel free to choose a preferred option and add it to the "Decision Outcome" section as well.
4. If making the proposed changes (e.g. to the API, schemas or examples) helps to explain your proposal, make those changes as well
5. Open a PR with your MADR document and any other changes

## Reviewing the proposal

During the review process, use PR comments to ask questions, make suggestions or generally discuss the proposal.
Alternatively, if a synchronous discussion takes place (e.g. an in-person or online meeting), add a description of what was discussed and the outcome into the ADR document itself.

Generally PRs should remain open for review for a period of time to invite comments from the wider TAMS community, and if necessary PRs should be circulated to interested individuals.
The maintainers at BBC R&D will facilitate this process, and expedite it if necessary

## Finishing and merging

Once the review process has completed and a consensus has been reached:

1. Amend the ADR document with relevant points from the review discussion, and changes to the decision if necessary
2. Try to make these changes with new commits, so it's possible to see the original version in the Git history
3. If you added an implementation at the same time, make the required changes there too.
   Rememeber to bump the API version in accordance with [the README](../../../README.md#api-versioning)
4. Amend the ADR status to "accepted"
5. Consider whether your rework would benefit from someone else looking over it
6. Merge the PR
