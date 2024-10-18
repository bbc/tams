all: help

venv:
	mkdir -p venv
	python -m venv venv
	. venv/bin/activate && pip install -r requirements.txt && deactivate

sample_content:
	./hls_sample_content.sh

env_exports:
	@echo "export OAUTH2_URL="
	@echo "export CLIENT_ID="
	@echo "export CLIENT_SECRET="
	@echo "export USERNAME="
	@echo "export PASSWORD="

clean:
	@rm -rf venv
	@rm -f bbb_sunflower_1080p_30fps_normal.mp4
	@rm -f bbb_sunflower_1080p_30fps_normal.mp4.zip
	@rm -rf sample_content

help:
	@echo "TAMS examples"
	@echo "make venv                - Prepare a Python virtual environment in venv/ for running the examples"
	@echo "make sample_content      - Download and prepare content into sample_content/"
	@echo "make env_exports         - Print environment variable exports that may used in the examples"
	@echo "make clean               - Delete files that were created"

.PHONY: all help clean env_exports
