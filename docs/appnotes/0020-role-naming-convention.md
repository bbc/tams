# 0020: Role Naming Convention

## Abstract

Each item in the collection of a multi-essence Source or Flow has a `role`, intended as a description of that item's purpose in the collection.
Roles are intended to be human-readable and uncontrolled, however a list of common editorial purposes and associated names is useful.

This functions much like [Tag Names](./0003-tag-names.md) and this list will likely grow over time.

## Editorial Purpose Names

## Video

| Name | Description |
| ---- | ----------- |
| `programme` | Primary, or default video for a piece of content, e.g. that will be edited or distributed on to the audience. |
| `signed` | Primary video with a signer in-vision. Consider using a label on the collected Source/Flow with the [language code](https://github.com/bbc/tams/blob/main/docs/appnotes/0003-tag-names.md#language_code) of the signer. |
| `cleanfeed` | Version of the video without graphics, for reversioning and re-use. |
| `video` | In a simple A/V mux that only contains the audio and video for an asset, the `role` provides little additional information, and calling it "video" may be sufficient. |

## Audio

_Note that in general, audio Flows and Sources should also use a [language code](https://github.com/bbc/tams/blob/main/docs/appnotes/0003-tag-names.md#language_code) label to allow clients to identify the language used._

| Name | Description |
| ---- | ----------- |
| `programme` | Primary, or default audio for a piece of content, e.g. that will be edited or distributed on to the audience. |
| `audio_description` | Audio description track. |
| `commentary` | Commentary track, where sent separately (e.g. from a sports event).  |
| `music&effects` | Music and Effects track, where sent separately. |
| `audio` | In a simple A/V mux that only contains the audio and video for an asset, the `role` provides little additional information, and calling it "audio" may be sufficient. |

In some cases it will also be appropriate to suffix channel labels for audio: for example if a stereo mix is set as two separate Flows, it may be referred to as `programme_L` and `programme_R`.
