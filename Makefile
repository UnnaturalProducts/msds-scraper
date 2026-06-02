RUN := poetry run
TAG := $(shell git log --format="%H" -n 1)

install:
	poetry install
	$(RUN) playwright install chromium

format:
	$(RUN) ruff check --select I --fix .
	$(RUN) ruff format

lint:
	$(RUN) ruff check .
	$(RUN) ruff format --check .

test:
	$(RUN) pytest -n auto

clean:
	fd -I "__pycache__" -x rm -rf && rm -rf .pytest_cache
