# 0023: Finding Flows to Play

## Abstract

This describes a possible algorithm a TAMS reader or player could follow to identify the best Flow to play for a given input ID, even when multiple Flows of a Source exist.

## Content

In the Source/Flow model used by TAMS, most editorial processes should work in terms of Sources, relating those to specific Flow representations only when necessary.
This Application Note lays out the process a TAMS player (or a reader in general) may follow to do so.

In general applications and components should be flexible.
The most user friendly approach tends to be accepting a single multi-essence Source (e.g. an A/V mux), locating suitable mono-essence Sources and then finding relevant Flows.
However some use cases will know exactly which Flows are required, e.g. because they have been selected by a rundown tool or MAM system.
And in some cases it will not be possible to "guess" accurately which Flows should be used.
The most flexible approach is therefore to allow both cases: accepting either a single Source, or a set of Flows.

When given a single Source ID:

1. `GET` the Source and check if it is multi-essence.
   If not, skip to step (3).
2. Get the details of collected Sources (`GET /sources?source_collected_by_ids=<given_source_id>`).
   Choose the correct Sources to play.  
    1. If there is only one of each type (e.g. one audio, one video) then these can be selected directly.  
    2. Otherwise select Sources where `role` is set to `programme` (from [AppNote0020 Editorial Purposes](./0020-editorial-purpose.md)) by default.  
    3. Otherwise select Sources where `role` is set to `video` or `audio` (according to type) by default.  
    4. Otherwise (or if a selected Source is multi-essence) the correct Source to play cannot be determined automatically.
       Provide a suitable error to the user and insist they be specific.  
3. For each selected mono-essence Source, list the Flows that represent that Source with `GET /flows?source=<selected_source_id>`.
   Apply any other relevant filtering (e.g. by coded, frame size, etc.)
4. Filter the returned list of Flows to remove any that do not meet requirements, such as codecs, containers or bitrates that are not readable by this system.
5. If constructing an adaptive bitrate (ABR) ladder for a suitable player, use this list to set quality steps in the player and stop here.
6. If `generation` is present, sort the list by `generation` in ascending order.
7. If `avg_bit_rate` is present, for each Flow with the same `generation` (or every Flow if `generation` is not present), sort the list by `avg_bit_rate` in descending order.
8. Choose the entry at the top of the list as the "best available" quality.

To read a given Flow ID, accounting for the possibility that `container_mapping` is used:

1. `GET` the Flow and check if `container` is set.
   If it is, skip to step 5, making a note of any `container_mapping` property on the Flow.
2. Check to see if the Flow is collected by a multi-essence Flow.
   Examine the Flows it is collected by (using `GET /flows?flows_collected_by_id=<this_flow_id>` to find one where `container` is set
3. Examine the `collects` property of the multi-essence Flow, and check the `container_mapping` to identify which track to filter out of the multi-essence Flow.
4. Get the list of segments using `GET /flows/<flowid>/segments`
5. Fetch each object, filter the relevant track (if `container_mapping` is used) and then remap timing as usual
