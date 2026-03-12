NUM_OF_PARENT:=$(shell echo $$(( $(words $(MAKEFILE_LIST)))) )
topdir:=$(realpath $(dir $(word $(NUM_OF_PARENT),$(MAKEFILE_LIST))))

# pbrversion calculates versions based on git tags, number of commits since the most recent tag, magic strings in commit messages to signal types of changes. Magic strings are of the form `Sem-Ver: ` followed by one of `feature`, `api-break`, `deprecation`, and `bugfix`. pbrversion returns a `<major>.<minor>.<patch>` semantic version. This repo only uses a `<major>.<minor>` version, so the last component is stripped using make's `basename` function.
NEXT_VERSION := $(basename $(shell docker run --rm -v $(topdir):/data:ro public.ecr.aws/o4o2s1w1/cloudfit/pbrversion:1.4.2 --brief))

all: help

render:
	$(MAKE) -C api/ $@

mock-server-up:
	$(MAKE) -C api/ $@

mock-server-down:
	$(MAKE) -C api/ $@

lint-markdown:
	docker run -v ${topdir}:/workdir davidanson/markdownlint-cli2-rules:v0.12.1

lint-apispec:
	$(MAKE) -C api/ lint

lint: lint-markdown lint-apispec

next-version:
	@echo $(NEXT_VERSION)

update-api-version:
	docker run --user="root" --rm -v "$(topdir)/api":/workdir mikefarah/yq e ".info.version = \"$(NEXT_VERSION)\" | .servers[1].variables.version.default = \"v$(NEXT_VERSION)\"" -i TimeAddressableMediaStore.yaml

help:
	@echo "tams-api"
	@echo "make render             - Generate HTML rendered version of OpenAPI document"
	@echo "make mock-server-up     - Start a mock API server on http://localhost:4010"
	@echo "make mock-server-down   - Stop the mock API server"
	@echo "make lint               - Lint API specification document and Markdown files"
	@echo "make next-version       - Print the version the code should have if it is released as it currently is"
	@echo "make update-api-version - Update the API version in the OpenAPI document to match the next-version. This WILL NOT make a release on the repository."

.PHONY: help render mock-server-up mock-server-down lint-markdown lint-apispec lint next-version update-api-version
