all: help

venv:
	mkdir -p venv
	python -m venv venv
	. venv/bin/activate && pip install -r requirements.txt && deactivate

env_exports:
	@echo "export OAUTH2_URL="
	@echo "export CLIENT_ID="
	@echo "export CLIENT_SECRET="
	@echo "export USERNAME="
	@echo "export PASSWORD="

clean:
	@rm -rf venv
	@rm -f bbb_sunflower_1080p_30fps_normal*
	@rm -f tams-edit-test-film.ts
	@rm -rf sample_content_segments
	@rm -rf sample_content

sample_content_segments:
	mkdir -p $@

tams-edit-test-film.ts:
	wget -O $@ https://object.lon1.bbcis.uk/a4c52e22f45b4a0fa3ea3b9a42b35808:test-content/tams-edit-test-film-v4.ts

bbb_sunflower_1080p_30fps_normal.mp4:
	curl -o bbb_sunflower_1080p_30fps_normal.mp4.zip -s https://download.blender.org/demo/movies/BBB/bbb_sunflower_1080p_30fps_normal.mp4.zip
	unzip -d . bbb_sunflower_1080p_30fps_normal.mp4.zip
	rm bbb_sunflower_1080p_30fps_normal.mp4.zip

sample_content_segments/hls_output.m3u8: bbb_sunflower_1080p_30fps_normal.mp4 sample_content_segments
	ffmpeg -i bbb_sunflower_1080p_30fps_normal.mp4 -c:v copy -muxdelay 0 -an -f hls -hls_time 5 -hls_playlist_type vod $@

sample_content_segments/wav_pcm_flow.list: tams-edit-test-film.ts sample_content_segments
	ffmpeg -i $< -vn -c:a pcm_s16le -f segment -segment_list $@ -segment_time 10 sample_content_segments/wav_pcm_flow_%03d.wav

sample_content_segments/mov_h264_flow.list: tams-edit-test-film.ts sample_content_segments
	ffmpeg -i $< -an -c:v copy -f segment -segment_list $@ -segment_time 60 sample_content_segments/mov_h264_flow_%03d.mov

fetch_sample_media: tams-edit-test-film.ts bbb_sunflower_1080p_30fps_normal.mp4

sample_content: sample_content_segments/hls_output.m3u8 sample_content_segments/wav_pcm_flow.list sample_content_segments/mov_h264_flow.list

help:
	@echo "TAMS examples"
	@echo "make venv                - Prepare a Python virtual environment in venv/ for running the examples"
	@echo "make fetch_sample_media  - Download sample media files"
	@echo "make sample_content      - Download and prepare content into sample_content_segments/"
	@echo "make env_exports         - Print environment variable exports that may used in the examples"
	@echo "make clean               - Delete files that were created"

.PHONY: all help clean env_exports fetch_sample_media sample_content
