.PHONY: dev-control doctor bundle edge-setup test

CLI=PYTHONPATH=cli python -m aion.cli

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
