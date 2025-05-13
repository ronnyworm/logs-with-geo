testa:
	pytest --cov=. --cov-report=html --show-capture=no tests/integration -s

test:
	pytest --cov=. --cov-report=html --show-capture=no tests/integration/test_main_flow.py -k 'test_main_output_just_one_line_with_location_not_found' -s

cov:
	open htmlcov/index.html

lint:
	@mv .venv ../.venv
	@-flake8 --max-line-length=150
	@mv ../.venv .venv
