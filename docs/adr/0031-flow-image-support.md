---
status: "draft"
---
# Add support for new flow type to support still images  

## Context and Problem Statement

Currently the TAMS API has three flow type: Video, Audio and Data.  There are a number of use cases around storing images on the flow timeline to represent where they have been extracted from the content.  These include UI elements, content navigation and VOD workflows.

Currently the nearest option is to treat these as non-continuous video and use the existing flow data model.  Separating out the images from the video will also aid discoverability and make it easier for readers to identify the content they want.  It is expected that different processes will be looking for the video (players) and images (ui components) and therefore not be interested in the other media type.  So separating the types will reduce the amount of work required to find the required content.

Most image workflows work with a single image that has been extracted from the video, there are scenarios where a mosaic of thumbnails could be required in a single image.  VOD trick play or AI analysis are examples of this type of workflow.  These have the added challenge of needing to store a manifest which describes the location of each thumbnail and the source timing.  There also may be scenarios where mosaics overlap with the content they contain and therefore break a core TAMS rule that segments should not overlap.

## Considered Options

- Option 1: Add new flow type to support single images
- Option 2: Add new flow type to support both single and mosaic style images
- Option 3: Do nothing and continue to put images under a video flow

## Decision Outcome

Recommended to do option 1 at this point and add basic image support in the TAMS API.  Since the mosaic use case is not clearly understood at this point in time then it is recommended that this gets parked until that time.  As it would be additional API fields then option 1 does not prevent this being added in the future.

### Implementation

See the API specification changes in PR [#122](https://github.com/bbc/tams/pull/122).

## Pros and Cons of the Options

### Option 1: Add new flow type to support single images

Add a new flow type to the TAMS specification to support single images only.

- Good: Provides simple method of storing and locating images
- Good: Correctly described content rather than trying to mis-use existing fields
- Good: Provides separation of essence parameters for video and still images so that in the future they can have new fields added independently
- Bad: TAMS is a basis in the NMOS specification for the flow types.  Since NMOS is for live video feeds then it has no concept of still images.  This ADR proposes using NMOS style terminology to describe the flow type as images, however this is technically not in the NMOS specification.

### Option 2: Add new flow type to support both single and mosaic style images

Add the image flow type from Option 1 plus optional metadata fields to describe the content of the mosaic.

- Bad: Full use case not completely clear whether it makes sense to hold mosaics in TAMS or create them downstream from images in the store

### Option 3: Do nothing and continue to put images under a video flow

Leave the existing functionality in place and continue to use the existing video flow type and metadata for still images

- Good - No changes required
- Bad - Mixes content types and makes locating correct flow required harder

