# Run with make push --file docker/django/Makefile -e VERSION=$(git rev-parse --short HEAD)
# Note that makefiles differentiate between tabs and spaces in a weird way!

# Ensure VERSION is set.
ifndef VERSION
$(error VERSION variable is not set. Use -e VERSION=XYZ to proceed.)
endif


REPO ?= freelawproject/bigcases2

# The various tags available
DOCKER_TAG_PROD = $(VERSION)-web-prod
WEB_PROD ?= latest-web-prod
WEB_DEV ?= latest-web-dev


.PHONY: all image push multiarch_image multiarch_push x86_image x86_push

UNAME := $(shell uname -m)

all: image

development:
	docker build --target web-dev -t $(REPO):$(WEB_DEV) --build-arg BUILD_ENV=dev --file docker/django/Dockerfile .

image:
	docker build --target web-prod -t $(REPO):$(DOCKER_TAG_PROD) -t $(REPO):$(WEB_PROD) --file docker/django/Dockerfile .
