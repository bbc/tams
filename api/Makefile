NUM_OF_PARENT:=$(shell echo $$(( $(words $(MAKEFILE_LIST)))) )
topdir:=$(realpath $(dir $(word $(NUM_OF_PARENT),$(MAKEFILE_LIST))))

JSON_FILES=$(shell find . -name "*.json")
LINT_JSON_TARGETS=$(patsubst %, %.lintjson, $(JSON_FILES))
LINT_JSONNODOCKER_TARGETS=$(patsubst %, %.lintnodockerjson, $(JSON_FILES))

all: help

%.lintjson:
	docker run -i ghcr.io/jqlang/jq:latest < $* '.' --indent 4 | diff $* -

%.lintnodockerjson:
	jq < $* '.' --indent 4 | diff $* -

lint-json-targets: $(LINT_JSONNODOCKER_TARGETS)

lint-jsonnodocker-targets: $(LINT_JSONNODOCKER_TARGETS)

build-lint-json:
	docker pull --platform linux/amd64 alpine >/dev/null 2>/dev/null || true
	DOCKER_BUILDKIT=1 docker build --platform linux/amd64 -f Dockerfile.multi --target jq -t tams_jq:local .

lint-json-mount: build-lint-json
	docker run --platform linux/amd64 --rm -v $(topdir):/api -w /api tams_jq:local /bin/sh -c 'set -x && for FILE in $(shell find . -name "*.json"); do jq < $$FILE '.' --indent 4 | diff $$FILE -; done'

lint-json-local:
	for FILE in $(shell find . -name "*.json"); do jq < $$FILE '.' --indent 4 | diff $$FILE -; done

lint-json:
	for FILE in $(shell find . -name "*.json"); do docker run -i ghcr.io/jqlang/jq:latest < $$FILE '.' --indent 4 | diff $$FILE -; done

conform-json:
	for FILE in $(shell find . -name "*.json"); do docker run -i ghcr.io/jqlang/jq:latest < $$FILE '.' --indent 4 > $$FILE.tmp.json && mv $$FILE.tmp.json $$FILE; done

build-lint-oas:
	docker pull --platform linux/amd64 stoplight/spectral:6.10 >/dev/null 2>/dev/null || true
	DOCKER_BUILDKIT=1 docker build --platform linux/amd64 -f Dockerfile.multi --target oaslint -t tams_api_oaslint:local .

# Work around https://github.com/stoplightio/spectral/issues/2819 using the bundled spec
lint-oas: build-lint-oas docs/TimeAddressableMediaStore_bundled.yaml
	docker run --platform linux/amd64 --rm -v $(topdir):/api tams_api_oaslint:local lint --fail-severity=warn /api/docs/TimeAddressableMediaStore_bundled.yaml

lint: lint-oas lint-json

build-bundle:
	docker pull redocly/cli:latest >/dev/null 2>/dev/null || true
	DOCKER_BUILDKIT=1 docker build -f Dockerfile.multi --target bundle -t tams_api_bundle:local .

docs/TimeAddressableMediaStore_bundled.yaml: build-bundle
	docker run --rm tams_api_bundle:local bundle /data/TimeAddressableMediaStore.yaml > $@

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
	@echo "make lint                - Lint API specification document, and json files"
	@echo "make conform-json        - Conform JSON files to linter"
	@echo "make render              - Generate HTML rendered version of OpenAPI document"
	@echo "make mock-server-up      - Start a mock API server on http://localhost:4010"
	@echo "make mock-server-down    - Stop the mock API server"
	@echo "make mock-server-healthy - Connect to mock API server, confirm it is working"

.PHONY: all lint-json conform-json build-lint-oas lint-oas lint build-bundle render mock-server-up mock-server-down mock-server-healthy help
