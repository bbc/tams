# Application Notes

This folder contains application notes in markdown format.
These documents provide ancillary information about the concepts in the TAMS API, and their application to real-world problems.
No part of these documents are considered part of the API specification, although including specification-type language as examples, or "opt-in" extensions is allowed.

There is a simple template [appnote-template.md](../templates/appnote-template.md) which describes the few restrictions there are on Application Notes.
Select a unique number for your Applcation Note, and try to keep them at least somewhat close together.

## Versioning

It is anticipated that these notes will change over time, therefore we need a way to refer to specific versions.
As these notes are stored in a git repository, we will make use of git commit IDs from the main branch to refer to a specific version.
For those unfamiliar with git, if you want to check if the versions you are looking at is the same as one referred to by someone else, the command

```shell
git diff <commit> <commit> -- <filename>
```

will indicate if there are differences between the verions or not.

If this versioning scheme presents you with problems, please raise an issue so we can investigate if another scheme would be more suitable.
