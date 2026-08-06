.PHONY: dev-control doctor bundle edge-setup test status logs restart start stop setup train train-ci guard model-all run-user run-pro run-ent claude-install claude-bootstrap claude-status desktop-dev desktop-build

PY ?= python3
CLI=$(PY) -m aion_core.cli

dev-control:
	PYTHONPATH=$(CURDIR) uvicorn control.app.main:app --reload --port 8000

doctor:
	bash scripts/doctor.sh

bundle:
	@tar czf deploy/bundles/example.tgz -C deploy/bundles/example .

edge-setup:
	sudo deploy/native/scripts/aion-edge-setup.sh

test:
	PYTHONPATH=$(CURDIR) pytest -q

APP_DIR ?= /opt/aion/OMERTAOS

status:
	systemctl status omertaos-control || true
	systemctl status omertaos-gateway || true
	systemctl status omertaos-console || true

logs:
	journalctl -u omertaos-control -n 50 --no-pager
	journalctl -u omertaos-gateway -n 50 --no-pager
	journalctl -u omertaos-console -n 50 --no-pager

restart:
	systemctl restart omertaos-control omertaos-gateway omertaos-console

start:
	systemctl start omertaos-control omertaos-gateway omertaos-console

stop:
	systemctl stop omertaos-control omertaos-gateway omertaos-console

setup:
	$(PY) -m pip install -U pip
	$(PY) -m pip install -e .[dev]

train:
	$(PY) scripts/train_eval.py --config policies/training.yaml

train-ci:
	$(PY) scripts/train_eval.py --config policies/training.yaml --ci

guard:
	$(PY) scripts/guard_generalization.py

model-all: setup train guard

run-user:
	AION_PROFILE=user docker compose --project-directory . -f deploy/docker/compose/full.yml up -d

run-pro:
	AION_PROFILE=professional docker compose --project-directory . -f deploy/docker/compose/full.yml up -d

run-ent:
	AION_PROFILE=enterprise-vip FEATURE_SEAL=1 docker compose --project-directory . -f deploy/docker/compose/full.yml up -d

# Developer quality gates
install-deps:
	$(PY) -m pip install --upgrade pip
	$(PY) -m pip install -r requirements.txt
	npm ci --prefix gateway
	npm ci --prefix console

lint:
	pre-commit run --all-files
	npm run lint --prefix gateway --if-present
	npm run lint --prefix console --if-present

verify:
	ci/verify.sh

structure-audit:
	$(PY) scripts/check_structure_consistency.py

# Docker Compose helpers for the quickstart stack
compose-up:
	docker compose --project-directory . -f deploy/docker/compose/quickstart.yml up --build -d

compose-down:
	docker compose --project-directory . -f deploy/docker/compose/quickstart.yml down

compose-clean:
	docker compose --project-directory . -f deploy/docker/compose/quickstart.yml down -v --remove-orphans

build-image:
	docker compose --project-directory . -f deploy/docker/compose/quickstart.yml build

bootstrap:
	./quick-install.sh

claude-install:
	bash scripts/claude/install-claude-code.sh

claude-bootstrap:
	bash scripts/claude/bootstrap-marketplace.sh

claude-status:
	bash scripts/claude/status.sh

desktop-dev:
	cd console/desktop-shell && npm run tauri:dev

desktop-build:
	cd console/desktop-shell && npm run tauri:build
