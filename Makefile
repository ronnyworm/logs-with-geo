.PHONY: build
build:
	docker build --platform linux/amd64 -t pyinstaller-builder .
	docker run --platform linux/amd64 --rm -v "$(PWD)/dist:/app/dist" pyinstaller-builder
	docker create --name extract-temp pyinstaller-builder
	docker cp extract-temp:/app/dist .
	docker rm extract-temp
	mv dist/main ./logs-with-geo
	chmod +x logs-with-geo

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
