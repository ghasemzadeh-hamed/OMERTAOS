.PHONY: dev-control doctor bundle edge-setup test status logs restart start stop setup train train-ci guard model-all

CLI=PYTHONPATH=cli python -m aion.cli
PY ?= python

dev-control:
	cd control && uvicorn app.main:app --reload --port 8001

doctor:
	$(CLI) doctor --verbose

bundle:
	@tar czf deploy/bundles/example.tgz -C deploy/bundles/example .

edge-setup:
	sudo deploy/scripts/aion_edge_setup.sh

test:
	pytest -q

APP_DIR ?= /opt/omerta/OMERTAOS

status:
	systemctl status omerta-control || true
	systemctl status omerta-gateway || true
	systemctl status omerta-console || true

logs:
	journalctl -u omerta-control -n 50 --no-pager
	journalctl -u omerta-gateway -n 50 --no-pager
	journalctl -u omerta-console -n 50 --no-pager

restart:
	systemctl restart omerta-control omerta-gateway omerta-console

start:
	systemctl start omerta-control omerta-gateway omerta-console

stop:
	systemctl stop omerta-control omerta-gateway omerta-console

setup:
	$(PY) -m pip install -U pip
	pip install -r requirements.txt

train:
	$(PY) scripts/train_eval.py --config policies/training.yaml

train-ci:
	$(PY) scripts/train_eval.py --config policies/training.yaml --ci

guard:
	$(PY) scripts/guard_generalization.py

model-all: setup train guard
