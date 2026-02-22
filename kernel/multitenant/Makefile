SHELL := /bin/bash

install:
	./scripts/install_linux.sh

run-user:
	PROFILE=user ./scripts/run_all.sh

run-pro:
	PROFILE=pro ./scripts/run_all.sh

run-ent:
	PROFILE=ent ./scripts/run_all.sh

clean:
	rm -rf .venv shared/gateway/node_modules shared/gateway/dist
	find shared -name "__pycache__" -type d -prune -exec rm -rf {} +
