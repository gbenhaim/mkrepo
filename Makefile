.PHONY: clean clean-test clean-pyc clean-build help install-user develop container container-static-version func-test
.DEFAULT_GOAL := help


define BROWSER_PYSCRIPT
import os, webbrowser, sys

try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT


define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT


define GET_CONTAINER_VERSION
	version=$$(python setup.py --version); \
	echo "$${version%+*}"
endef


BROWSER := python -c "$$BROWSER_PYSCRIPT"
REG_AND_REPO := quay.io/mkrepo
LATEST_TAG := $(REG_AND_REPO):latest
STATIC_TAG = $(REG_AND_REPO):$(shell $(GET_CONTAINER_VERSION))

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

lint: ## check style with flake8
	flake8 mkrepo tests

unit-test: ## run tests quickly with the default Python
	pytest -sv tests/unit

func-test:
	tests/func/func-tests.sh $(IMAGE)

test-all: ## run tests on every Python version with tox
	tox

coverage: ## check code coverage quickly with the default Python
	coverage run --source mkrepo -m pytest
	coverage report -m
	coverage html
	$(BROWSER) htmlcov/index.html

dist: clean ## builds source and wheel package
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist

install: clean ## install the package to the active Python's site-packages
	python setup.py install

install-user: clean
	python setup.py install --user

develop: clean
	python setup.py develop

container: dist
	docker build -t $(LATEST_TAG) .
	docker tag $(LATEST_TAG) $(STATIC_TAG)

container-static-version:
	@echo $(STATIC_TAG)

