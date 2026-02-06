# 0020: Role Naming

## Abstract

Each item in the collection of a multi-essence Source or Flow has a `role`, intended as a description of that item's purpose in the collection.
Roles are intended to be human-readable, and clients may choose whether to get the details of each item in the collection and decide how to use it (e.g. what to present to the user) from there, or may decide to use the roles directly.
In addition there are some common structures of Flows and Sources that come up in a lot of workflows, such as those laid out in the [multi-essence collection application note](./0001-multi-mono-essence-flows-sources.md).
In these particular cases a semi-structured naming convention is useful, and this document describes an approach and captures some possible terms and their meaning.

This approach is similar to the one taken for [storage backend labels](./0009-storage-label-format.md) and [tags](./0003-tag-names.md).

## Role Structure

A structured role captures multiple pieces of information:
- The type of content (also captured in the `format` property)
- The editorial purpose of the content (may be captured in `label`, `description` or tags)
