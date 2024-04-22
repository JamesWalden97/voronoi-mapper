.PHONY: lint check

check:
	@echo "Running black..."
	poetry run black --check .
	@echo "Running isort..."
	poetry run isort -c .

lint:
	@echo "Running black..."
	poetry run black .
	@echo "Running isort..."
	poetry run isort .

test:
	poetry run pytest . --cov --cov-report term-missing

