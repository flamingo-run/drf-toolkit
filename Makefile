setup:
	@pip install -U pip poetry

dependencies:
	@make setup
	@poetry install --no-root

update:
	@poetry update

test:
	@make check
	@make lint
	@make unit

check:
	@echo "Checking safety and integrity ..."
	poetry check
	poetry run safety check

lint:
	@echo "Checking code style ..."
	DJANGO_SETTINGS_MODULE=test_app.settings APP_NAME=sample-app ENV=test poetry run pylint ./drf_kit ./test_app
	poetry run black --check .
	poetry run isort --check .

style:
	@echo "Applying code style ..."
	poetry run black .
	poetry run isort .


unit:
	@echo "Running unit tests ..."
	ENV=test poetry run coverage run test_app/manage.py test --no-input

clean:
	@rm -rf .coverage coverage.xml dist/ build/ *.egg-info/

publish:
	@make clean
	@printf "\nPublishing lib"
	@make setup
	@poetry config pypi-token.pypi $(PYPI_API_TOKEN)
	@poetry publish --build
	@make clean


.PHONY: setup dependencies update test check lint style unit clean publish
