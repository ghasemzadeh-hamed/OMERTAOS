.PHONY: dev-control doctor bundle edge-setup test status logs restart start stop setup train train-ci guard model-all run-user run-pro run-ent

PY ?= python3
CLI=$(PY) -m aionos_core.cli

dev-control:
	cd control && PYTHONPATH=$(CURDIR):$(CURDIR)/os uvicorn os.control.main:app --reload --port 8001

doctor:
	$(CLI) doctor

bundle:
	@tar czf deploy/bundles/example.tgz -C deploy/bundles/example .

edge-setup:
	sudo deploy/scripts/aion_edge_setup.sh

test:
	PYTHONPATH=$(CURDIR) pytest -q

APP_DIR ?= /opt/aionos/OMERTAOS

status:
	systemctl status aionos-control || true
	systemctl status aionos-gateway || true
	systemctl status aionos-console || true

logs:
	journalctl -u aionos-control -n 50 --no-pager
	journalctl -u aionos-gateway -n 50 --no-pager
	journalctl -u aionos-console -n 50 --no-pager

restart:
	systemctl restart aionos-control aionos-gateway aionos-console

start:
	systemctl start aionos-control aionos-gateway aionos-console

stop:
	systemctl stop aionos-control aionos-gateway aionos-console

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
	AION_PROFILE=user docker compose -f docker-compose.yml up -d

run-pro:
        AION_PROFILE=professional docker compose -f docker-compose.yml up -d

run-ent:
        AION_PROFILE=enterprise-vip FEATURE_SEAL=1 docker compose -f docker-compose.yml up -d

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

# Docker Compose helpers for the quickstart stack
compose-up:
	docker compose -f docker-compose.quickstart.yml up --build -d

compose-down:
	docker compose -f docker-compose.quickstart.yml down

compose-clean:
	docker compose -f docker-compose.quickstart.yml down -v --remove-orphans

build-image:
	docker compose -f docker-compose.quickstart.yml build
