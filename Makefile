RUN := poetry run
TAG := $(shell git log --format="%H" -n 1)

format:
	$(RUN) isort ./msds_scraper ./tests
	$(RUN) black ./msds_scraper ./tests

test:
	$(RUN) pytest

clean:
	fd -I "__pycache__" -x rm -rf && rm -rf .pytest_cache
