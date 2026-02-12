all: help

venv:
	mkdir -p venv
	python -m venv venv
	. venv/bin/activate && pip install -r requirements.txt && deactivate

testvenv:
	mkdir -p testvenv
	python -m venv testvenv
	. testvenv/bin/activate && pip install -r test-requirements.txt -r requirements.txt && deactivate

env_exports:
	@echo "export API_URL="
	@echo "export JWKS_URL="
	@echo "export GROUP_CLAIM="

run: venv
	. venv/bin/activate && sanic api:app ; deactivate

lint: testvenv
	. testvenv/bin/activate && flake8 ; deactivate

typecheck: testvenv
	. testvenv/bin/activate && mypy api.py ; deactivate

clean:
	@rm -rf venv
	@rm -rf testvenv
	@rm -rf .mypy_cache
	@rm -rf __pycache__
	@rm -rf .python-version

help:
	@echo "TAMS Authorisation Proxy Example"
	@echo "make venv        - Prepare a Python virtual environment in venv/ for running the examples"
	@echo "make testvenv    - Prepare a Python virtual environment in testvenv/ for running the tests"
	@echo "make env_exports - Print environment variable exports that may used in the examples"
	@echo "make run         - Start the auth proxy"
	@echo "make lint        - Lint the source code"
	@echo "make typecheck   - Typecheck the source code"
	@echo "make clean       - Delete files that were created"

.PHONY: all help clean env_exports run lint typecheck
