# 0025: Editorial Purpose

## Abstract

An `editorial_purpose` tag is defined in [AppNote 0003: Tag Names](./0003-tag-names.md) to give a hint about what a particular Source or Flow contains and how it could be used.
The tag's values are primarily intended to be human-readable and uncontrolled, however this list provides suggested values and their meanings to allow some commonality.
Much like other tag definitions in TAMS, the list can be amended and will likely grow over time: implementers may prefix an implementation-specific value along the lines of `_<service_name>_<editorial purpose>`, but should consider expanding this list.

## Editorial Purposes

## Video

| Name | Description |
| ---- | ----------- |
| `programme` | Primary, or default video for a piece of content, e.g. that will be edited or distributed on to the audience. |
| `programme_signed` | Primary video with a signer in-vision. Consider using a label on the collected Source/Flow with the [language code](https://github.com/bbc/tams/blob/main/docs/appnotes/0003-tag-names.md#language_code) of the signer. |
| `cleanfeed` | Version of the video without graphics, for reversioning and re-use. |

## Audio

For audio SMPTE ST377-41 provides a rich vocabulary for audio content, which can be used directly by TAMS.
A number of common examples are reproduced here: for the full list see _Section 5.4 MCA Content_ in [ST377-41:2023](https://pub.smpte.org/doc/st377-41/): by convention TAMS uses the "MCA Content" name (rather than the Symbol value), lowercased with underscores in place of spaces.

_Note that in general, audio Flows and Sources should also use a [language code](https://github.com/bbc/tams/blob/main/docs/appnotes/0003-tag-names.md#language_code) label to allow clients to identify the language used._

| Name | Description |
| ---- | ----------- |
| `primary` | Primary, or default audio for a piece of content, e.g. that will be edited or distributed on to the audience. |
| `descriptive_video` | Audio description track, mixed with primary programme content for presentation to visually impaired audiences. |
| `visually_impaired` | Audio description track, not mixed with the primary programme content. |
| `live_commentary` | Commentary track, where sent separately (e.g. from a sports event).  |
| `music_and_effects` | Music and Effects track, where sent separately. |
| `audio` | In a simple A/V mux that only contains the audio and video for an asset, the `role` provides little additional information, and calling it "audio" may be sufficient. |

## Data

| Name | Description |
| ---- | ----------- |
| `sdh` | Subtitles for the Deaf and Hard of Hearing, including descriptive information of audio cues and other non-dialogue sound |
| `transcript` | Subtitles containing only the spoken words |
