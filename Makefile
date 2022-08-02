setup:
	@pip install -U pip poetry

dependencies: setup
	@poetry install --no-root

update:
	@poetry update

test: check lint unit

check:
	@poetry check

lint:
	@echo "Checking code style ..."
	DJANGO_SETTINGS_MODULE=test_app.settings poetry run pylint ./*/*.py
	poetry run black --check .

unit:
	@echo "Running unit tests ..."
	ENV=test poetry run coverage run test_app/manage.py test --no-input

clean:
	@rm -rf .coverage coverage.xml dist/ build/ *.egg-info/

publish: clean setup
	@printf "\nPublishing lib"
	@poetry config pypi-token.pypi $(PYPI_API_TOKEN)
	@poetry publish --build
	@make clean


.PHONY: lint publish clean unit test dependencies setup
