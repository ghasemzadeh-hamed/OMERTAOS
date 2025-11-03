.PHONY: install install-extras run lint test

install:
	pip install --upgrade pip setuptools wheel
	pip install -e .

install-extras:
	@[ -z "$$EXTRAS" ] && echo "Set EXTRAS=list (e.g. ml-explain,ml-optim)" && exit 1 || true
	pip install -e .[$$EXTRAS]

run:
	uvicorn aionos_control.main:app --host 0.0.0.0 --port 8080 --reload

lint:
	ruff --fix .
	mypy aionos_control || true

test:
	pytest -q
