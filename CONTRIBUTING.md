# Contributing

Thank you for your interest in our work.
If you're more generally interested in our Time Addressable Media Stores work, the implementations we've built internally or opportunities for collaboration, please reach out to us at <cloudfit-opensource@rd.bbc.co.uk>

## API Improvements

We welcome suggestions for changes and improvements to the API.
Feel free to reach out using the email address above, or alternatively open a GitHub Issue.

## Submitting Changes

If you've fixed a problem or thought of an improvement, feel free to fork the repository and submit a Pull Request in the usual way.
The process is:

1. Fork the repository
2. For more significant changes, consider starting with writing an ADR document: see [the ADR readme](./docs/adr/README.md) for more
3. Make, commit and push changes to a branch on your fork
   - Make sure the commit message contains your email address
   - Where appropriate, make sure your commit messages includes a line with one of the following:
      - `sem-ver: api-break` - where a breaking change is made
      - `sem-ver: feature` - where a new feature has been added
      - `sem-ver: deprecation` - where an existing feature has been marked as deprecated, but not yet removed
4. If you haven't already done so, sign the CLA (see below)
5. Prior to opening a Pull Request you may wish to run the linter with `make lint`: see [Development](./README.md#development) for more on the targets available
6. Open a Pull Request with your changes.
   Don't worry about leaving empty spaces on the PR template (it's aimed at internal contributions), just fill in the description.
   A maintainer will review your changes, and trigger the CI process.

## Contributor Licence Agreement (CLA)

We desire that contributors of pull requests have signed, and submitted by email, an [Individual Contributor Licence Agreement (ICLA)](./ICLA.md), which is based on the Apache CLA.

The purpose of this agreement is to clearly define the terms under which intellectual property has been contributed to the BBC and thereby allow us to defend the project should there be a legal dispute regarding the software at some future time.

If you haven't signed and emailed the agreement yet then the project owners will contact you using the contact info with the pull request.
