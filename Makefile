.DEFAULT_GOAL = help
.PHONY: help setup test build publish docs docs-serve clean

PYTHON ?= "python3"
UV ?= "uv"

help:
	@echo --HELP--
	@echo make help - display this message
	@echo make setup - setup development environment "("requires uv")"
	@echo make test - run tests
	@echo make build - build package
	@echo make publish - upload package to pypi
	@echo make docs - build documentation
	@echo make docs-serve - build and serve documentation
	@echo make clean - remove build artifacts

setup:
	@echo --SETUP--
	${UV} venv
	${UV} pip compile pyproject.toml --all-extras -o requirements-dev.txt
	${UV} pip sync requirements-dev.txt

test: setup
	@echo --TEST--
	@echo placeholder

build: setup
	@echo --BUILD--
	${PYTHON} -m build

publish: build
	@echo --PUBLISH--
	${PYTHON} -m twine upload dist/*

docs: setup
	@echo --DOCS--
	${PYTHON} -m pdoc simplematrixbotlib -o docs --mermaid

docs-serve: setup
	@echo --DOCS--
	${PYTHON} -m pdoc simplematrixbotlib --port 8000 --mermaid

clean:
	@echo --CLEAN--
	rm -rdf simplematrixbotlib.egg-info
	rm -rdf dist
