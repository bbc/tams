NUM_OF_PARENT:=$(shell echo $$(( $(words $(MAKEFILE_LIST)))) )
topdir:=$(realpath $(dir $(word $(NUM_OF_PARENT),$(MAKEFILE_LIST))))

all: lint render

build-lint:
	docker pull ap-docker.artifactory.labs.bbc/cloudfit/cloudfit_base:latest >/dev/null 2>/dev/null || true
	DOCKER_BUILDKIT=1 docker build -f Dockerfile.multi --build-arg VERSION=0.0.1 --build-arg BUILD_TAG=local --build-arg CLOUDFIT_BASE_NAME=ap-docker.artifactory.labs.bbc/cloudfit/cloudfit_base --build-arg CLOUDFIT_BASE_LABEL=latest  --target oasvalidate -t tams_api_oasvalidate:local .

lint: build-lint
	docker run --rm  -ti tams_api_oasvalidate:local lint /data/TimeAddressableMediaStore.yaml


build-render:
	docker pull ap-docker.artifactory.labs.bbc/cloudfit/cloudfit_base:latest >/dev/null 2>/dev/null || true
	DOCKER_BUILDKIT=1 docker build -f Dockerfile.multi --build-arg VERSION=0.0.1 --build-arg BUILD_TAG=local --build-arg CLOUDFIT_BASE_NAME=ap-docker.artifactory.labs.bbc/cloudfit/cloudfit_base --build-arg CLOUDFIT_BASE_LABEL=latest  --target oasrender -t tams_api_oasrender:local .

render: build-render
	docker run --rm  -ti -v "${topdir}/docs:/docs" tams_api_oasrender:local bundle /data/TimeAddressableMediaStore.yaml -o /docs/TimeAddressableMediaStore.html


mock-server-up:
	docker pull stoplight/prism >/dev/null 2>/dev/null || true
	docker run --rm --init --name mock-tams -v "${topdir}":/data:ro -p 4010:4010 stoplight/prism mock /data/TimeAddressableMediaStore.yaml -h 0.0.0.0

mock-server-down:
	docker stop mock-tams

mock-server-healthy:
	@echo Getting \"/\" using \"tams:tams\" credentials to check service is healthy:
	@curl -u tams:tams http://localhost:4010
	@echo


.PHONY: all build-lint lint build-render render mock-server-up mock-server-down mock-server-healthy
