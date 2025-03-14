test:
	pytest --cov=. --cov-report=html --show-capture=no tests/integration -s

lint:
	mv .venv ../.venv
	-flake8 --max-line-length=150
	mv ../.venv .venv
