#!/bin/bash

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)

if [ ! -f ${SCRIPT_DIR}/bbb_sunflower_1080p_30fps_normal.mp4 ]
then
    curl -o ${SCRIPT_DIR}/bbb_sunflower_1080p_30fps_normal.mp4.zip -s https://download.blender.org/demo/movies/BBB/bbb_sunflower_1080p_30fps_normal.mp4.zip
    unzip -d ${SCRIPT_DIR} ${SCRIPT_DIR}/bbb_sunflower_1080p_30fps_normal.mp4.zip
fi

mkdir -p ${SCRIPT_DIR}/sample_content

# The '-muxdelay 0' option below is used to avoid the 1.4 second delay added by the ffmpeg mpegts muxer.
# Note that the presentation start time of bbb_sunflower_1080p_30fps_normal.mp4 is 0.066667, not 0.

ffmpeg -i ${SCRIPT_DIR}/bbb_sunflower_1080p_30fps_normal.mp4 -c:v copy -muxdelay 0 -an -f hls -hls_time 5 -hls_playlist_type vod ${SCRIPT_DIR}/sample_content/hls_output.m3u8
