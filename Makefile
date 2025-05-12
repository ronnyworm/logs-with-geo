test:
	pytest --cov=. --cov-report=html --show-capture=no tests/integration -s
	# pytest --cov=. --cov-report=html --show-capture=no tests/integration/test_main_flow.py -k 'test_main_output_ip_field1_nginx_guess' -s

lint:
	@mv .venv ../.venv
	@-flake8 --max-line-length=150
	@mv ../.venv .venv
