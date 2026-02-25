.PHONY: lint

lint:
	python3 -m compileall -q scopes/skills/*/scripts
