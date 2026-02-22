.PHONY: lint

lint:
	python3 -m compileall -q skills/*/scripts
