
all: help

render:
	$(MAKE) -C api/ $@

mock-server-up:
	$(MAKE) -C api/ $@

mock-server-down:
	$(MAKE) -C api/ $@

help:
	@echo "tams-api"
	@echo "make render           - Generate HTML rendered version of OpenAPI document"
	@echo "make mock-server-up   - Start a mock API server on http://localhost:4010"
	@echo "make mock-server-down - Stop the mock API server"

.PHONY: help render mock-server-up mock-server-down
