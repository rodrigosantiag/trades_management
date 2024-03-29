# Makefile version 22.01.19.1

# github env vars
ifeq ($(GITHUB_REF), refs/heads/main)
	ENVIRONMENT ?= production
endif
ifeq ($(GITHUB_REF), refs/heads/staging)
	ENVIRONMENT ?= staging
endif

# project settings
PROJECT_NAME  := $(shell grep -m1 'APPNAME' */settings.py | cut -f2 -d'"')
PROJECT_PATH  := $(shell ls */settings.py | xargs dirname | head -n 1)
ENVIRONMENT   ?= development
STACK_NAME    ?= "$(PROJECT_NAME)-$(ENVIRONMENT)-stack"
STACK_BUCKET  ?= "trades-management-$(ENVIRONMENT)-artifacts"

# venv settings
export PYTHONPATH := $(PROJECT_PATH):tests/fixtures
export VIRTUALENV := $(PWD)/.venv
export PATH       := $(VIRTUALENV)/bin:$(PATH)

# unittest logging level
test: export LOG_LEVEL=CRITICAL

# dockerfile settings if present
ifeq ($(wildcard Dockerfile),)
deploy: AWS_ACCOUNT_ID = $(shell aws sts get-caller-identity --output text --query Account)
deploy: AWS_ECR_DOMAIN = $(AWS_ACCOUNT_ID).dkr.ecr.us-east-1.amazonaws.com
deploy: SAM_EXTRA_ARGS = --image-repository $(AWS_ECR_DOMAIN)/$(PROJECT_NAME)
endif

# fix make < 3.81 (macOS and old Linux distros)
ifeq ($(filter undefine,$(value .FEATURES)),)
SHELL = env PATH="$(PATH)" /bin/bash
endif

.PHONY: .env .venv

all:

.env:
	echo 'PYTHONPATH="$(PYTHONPATH)"' > .env

.venv:
	python3.8 -m venv $(VIRTUALENV)
	pip install --upgrade pip

clean:
	rm -rf dependencies .pytest_cache .coverage .aws-sam
	find $(PROJECT_PATH) -name __pycache__ | xargs rm -rf
	find tests -name __pycache__ | xargs rm -rf

install-hook:
	@echo "make lint" > .git/hooks/pre-commit
	@chmod +x .git/hooks/pre-commit

install-dev: .venv .env install install-hook
	if [ -f requirements-dev.txt ]; then pip install -r requirements-dev.txt; fi

install:
	if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

lint:
	black --line-length=100 --target-version=py38 --check .
	flake8 --max-line-length=100 --ignore=E402,W503,E712 --exclude .venv,dependencies
	@if [ -f swagger.yml ]; then openapi-spec-validator swagger.yml; fi

format:
	black --line-length=100 --target-version=py38 .

test-integration:
	python -m unittest discover -p "itest*.py"

test:
	coverage run --source=$(PROJECT_PATH) --omit=dependencies -m unittest

coverage: test .coverage
	coverage report -m --fail-under=90

migrate:
	aws lambda invoke --function-name $(PROJECT_NAME)-migrations result --log-type Tail > output
	@jq -r '.LogResult' output | base64 -d
	@HAS_ERROR=$$(jq 'has("FunctionError")' output) ; ! $$HAS_ERROR

deploy:
	pip install -r requirements.txt -t .aws-sam/dependencies/python
	sam deploy \
		--stack-name $(STACK_NAME) \
		--s3-bucket $(STACK_BUCKET) \
		--template-file template.yml \
		--capabilities CAPABILITY_IAM \
		--tags "stack=$(PROJECT_NAME)" \
		$(SAM_EXTRA_ARGS)
