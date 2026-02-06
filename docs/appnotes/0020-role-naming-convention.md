# 0020: Role Naming Convention

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
- Where necessary, a sub-identifier where multiple items fulfil a related editorial purpose (again, may be captured in `label`, `description` or tags)

The general structure of a role is:

```text
<type>:<purpose[optional]>:<sub-id[optional]>
```

For example a complex package of material might contain the following roles:

```text
video:programme
video:signed:bsi
audio:programme:eng
audio:programme:fra
audio:audio_description
subtitles::eng
subtitles::fra
```

Here multiple languages of programme audio are provided, with the language is called out as a sub-identifier (and will also be present in the `language_code` tag).
In addition a signed version of the video and an audio description track are included.
Finally the subtitles appear in multiple languages, however there is no further editorial purpose beyond the type, so the feld is left blank.

In a much simpler example of an A/V mux ingest, the additional information may not be necessary, and the roles could be as simple as:

```text
video
audio
```

Depending on how the content is structured, the audio could take the form of a collection of mono channels, which might be described as:

```text
audio:right
audio:left
audio:center
audio:left-surround
audio:right-surround
audio:lfe
```

## Editorial Purpose Names

## Video

| Name | Description |
| ---- | ----------- |
| `programme` | Primary, or default video for a piece of content, e.g. that will be edited or distributed on to the audience |
| `signed` | Primary video with a signer in-vision. Consider using a sub-identifier for the language code of the signer (e.g. `bsi`) |
| `cleanfeed` | Version of the video without graphics, for reversioning and re-use |

## Audio

| Name | Description |
| ---- | ----------- |
| `programme` | Primary, or default audio for a piece of content, e.g. that will be edited or distributed on to the audience. Consider using a sub-identifier for the language code. |
| `audio_description` | Audio description track. Consider using a sub-identifier for the language code. |
| `commentary` | Commentary track, where sent separately (e.g. from a sports event).  Consider using a sub-identifier for the language code. |
| `music&effects` | Music and Effects track, where sent separately |
