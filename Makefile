.PHONY: build-dev
build-dev: ##build the image
	docker build -f app/DockerfileDev -t tms-dev ./app

.PHONY: run-dev
run-dev: ## start the container
	docker run -d \
	-v $(pwd)/app:/app \
	-p 8054:8000 \
	--rm --name tms-dev-container \
	tms-dev 

.PHONY: exec
exec: ## run the container
	docker exec -it \
	tms-dev-container bash

.PHONY: build-prod
build-prod: ##build the production image
	docker build -f app/Dockerfile -t tms-prod ./app

.PHONY: deploy-local
deploy-local: ##deploy to local k3s cluster
	kubectl apply -f infrastructure/argocd-app.yaml

.PHONY: setup-infra
setup-infra: ##setup infrastructure on EC2
	cd infrastructure && chmod +x setup-ec2-k3s.sh && sudo ./setup-ec2-k3s.sh

.PHONY: quick-deploy
quick-deploy: ##quick deployment
	cd infrastructure && chmod +x quick-start.sh && ./quick-start.sh

.PHONY: help
help: ##show this help
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
	