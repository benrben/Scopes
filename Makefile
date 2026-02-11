.PHONY: lint

lint:
	python3 scripts/lint_prompts.py
	python3 scripts/lint_package.py
