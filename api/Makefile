NUM_OF_PARENT:=$(shell echo $$(( $(words $(MAKEFILE_LIST)))) )
topdir:=$(realpath $(dir $(word $(NUM_OF_PARENT),$(MAKEFILE_LIST))))

all: help


build-lint:
	docker pull --platform linux/amd64 stoplight/spectral:6.10 >/dev/null 2>/dev/null || true
	DOCKER_BUILDKIT=1 docker build --platform linux/amd64 -f Dockerfile.multi --target oaslint -t tams_api_oaslint:local .

lint: build-lint
	docker run --platform linux/amd64 --rm tams_api_oaslint:local lint --fail-severity=warn /data/TimeAddressableMediaStore.yaml


build-bundle:
	docker pull redocly/cli:latest >/dev/null 2>/dev/null || true
	DOCKER_BUILDKIT=1 docker build -f Dockerfile.multi --target bundle -t tams_api_bundle:local .

docs/TimeAddressableMediaStore_bundled.yaml: build-bundle
	docker run --rm  tams_api_bundle:local bundle /data/TimeAddressableMediaStore.yaml > $@

render: docs/TimeAddressableMediaStore_bundled.yaml


mock-server-up:
	docker pull --platform linux/amd64 stoplight/prism >/dev/null 2>/dev/null || true
	docker run --platform linux/amd64 --rm --init --name mock-tams -v "${topdir}":/data:ro -p 4010:4010 stoplight/prism mock /data/TimeAddressableMediaStore.yaml -h 0.0.0.0

mock-server-down:
	docker stop mock-tams

mock-server-healthy:
	@echo Getting \"/\" using \"tams:tams\" credentials to check service is healthy:
	@curl -u tams:tams http://localhost:4010
	@echo


help:
	@echo "tams-api"
	@echo "make lint                - Lint API specification document"
	@echo "make render              - Generate HTML rendered version of OpenAPI document"
	@echo "make mock-server-up      - Start a mock API server on http://localhost:4010"
	@echo "make mock-server-down    - Stop the mock API server"
	@echo "make mock-server-healthy - Connect to mock API server, confirm it is working"

.PHONY: all build-lint lint build-bundle render mock-server-up mock-server-down mock-server-healthy help
