.PHONY: clean lint test mutate help frontend backend

# Default argument when none are provided
.DEFAULT_GOAL := help

# To inform the user of the available commands.
help:
	@echo "Available commands:"
	@echo "  make lint       - Run static code analysis using pylint"
	@echo "  make test       - Run the pytest test suite"
	@echo "  make mutate     - Run mutmut mutation testing"
	@echo "  make clean      - Remove build, cache, test, and python artifacts"
	@echo "  make run      	 - Modifies the SQL database, without reinitializing the database"
	@echo "  make init       - Modifies the SQL database, after reinitializing the database"

# To properly clean up the files that might get in the way of the user or other commands.
clean:
	@echo "Cleaning up unwanted files and test artifacts..."
	@rm -rf .pytest_cache/
	@rm -rf .coverage *.coverage
	@rm -rf mutants/
	@rm -rf htmlcov/
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@echo "Clean complete."

# To run the frontend code
frontend:
	@echo "Running FrontEnd"
	@./run_frontend.sh
	@echo "Done"

# To run the backend code
backend:
	@echo "Running BackEnd"
	@./run_backend.sh
	@echo "Done"

# To statically analyze the code.
lint:
	@echo "Running static analysis..."
	@chmod +x run_pylint.sh
	@echo ./run_pylint.sh
	@./run_pylint.sh || true
	@echo "Static Analysis Complete."

# To run the provided tests classes.
test: clean
	@echo "Running test suite..."
	@chmod +x run_pytest.sh
	@echo ./run_pytest.sh
	@./run_pytest.sh || true
	@echo "Test Suite Complete"

# To run a mutation test on the code.
mutate: clean
	@echo "Running mutation tests..."
	@echo mutmut run
	@mutmut run || true
