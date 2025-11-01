.PHONY: dev doctor bundle test-api

CONTROL_DIR=control
CLI=PYTHONPATH=cli python -m aion.cli


dev:
cd $(CONTROL_DIR) && poetry run uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

doctor:
$(CLI) doctor --verbose

bundle:
@mkdir -p dist
tar -czf dist/example-bundle.tgz -C deploy/bundles/example my-config

test-api:
cd $(CONTROL_DIR) && poetry run pytest -q tests/api
