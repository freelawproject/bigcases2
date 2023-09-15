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
RQ_TAG = $(VERSION)-rq
RQ_LATEST ?= latest-rq


.PHONY: all image push multiarch_image multiarch_push x86_image x86_push

UNAME := $(shell uname -m)

all: image

image:
	docker build --target web-prod -t $(REPO):$(DOCKER_TAG_PROD) -t $(REPO):$(WEB_PROD) --file docker/django/Dockerfile .
	docker build --target rq -t $(REPO):$(RQ_TAG) -t $(REPO):$(RQ_LATEST) --file docker/django/Dockerfile .

push: image
	$(info Checking if valid architecture)
	@if [ $(UNAME) = "x86_64" ]; then \
	    echo "Architecture is OK. Pushing.";\
	    docker push $(REPO):$(DOCKER_TAG_PROD);\
		docker push $(REPO):$(RQ_TAG);\
		docker push $(REPO):$(RQ_LATEST);\
	else \
		echo "Only x86_64 machines can push single-architecture builds. If you want to \
push a build, try 'make multiarch_push', which builds for both arm64 and amd64. This \
protects against arm64 builds being accidentally deployed to the server (which uses x86_64).";\
	fi

multiarch_image:
	export DOCKER_CLI_EXPERIMENTAL=enabled
	docker buildx rm
	docker buildx create --use --name flp-builder
	docker buildx build --platform linux/amd64,linux/arm64 -t $(REPO):$(WEB_PROD) -t $(REPO):$(DOCKER_TAG_PROD) --file docker/django/Dockerfile .
	docker buildx build --platform linux/amd64,linux/arm64 -t $(REPO):$(RQ_LATEST) -t $(REPO):$(RQ_TAG) --file docker/django/Dockerfile .

multiarch_push:
	docker buildx build --push --platform linux/amd64,linux/arm64 -t $(REPO):$(WEB_PROD) -t $(REPO):$(DOCKER_TAG_PROD) --file docker/django/Dockerfile .
	docker buildx build --push --platform linux/amd64,linux/arm64 -t $(REPO):$(RQ_LATEST) -t $(REPO):$(RQ_TAG) --file docker/django/Dockerfile .

x86_push:
	export DOCKER_CLI_EXPERIMENTAL=enabled
	docker buildx rm
	docker buildx create --use --name flp-builder
	docker buildx build --push --platform linux/amd64 -t $(REPO):$(WEB_PROD) -t $(REPO):$(DOCKER_TAG_PROD) --file docker/django/Dockerfile .
	docker buildx build --push --platform linux/amd64 -t $(REPO):$(RQ_LATEST) -t $(REPO):$(RQ_TAG) --file docker/django/Dockerfile .
