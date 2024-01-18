NUM_OF_PARENT:=$(shell echo $$(( $(words $(MAKEFILE_LIST)))) )
topdir:=$(realpath $(dir $(word $(NUM_OF_PARENT),$(MAKEFILE_LIST))))

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

help:
	@echo "tams-api"
	@echo "make render           - Generate HTML rendered version of OpenAPI document"
	@echo "make mock-server-up   - Start a mock API server on http://localhost:4010"
	@echo "make mock-server-down - Stop the mock API server"
	@echo "make lint             - Lint API specification document and Markdown files"

.PHONY: help render mock-server-up mock-server-down
