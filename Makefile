PYTHON ?= python3

.PHONY: install run check test

install:
	$(PYTHON) -c 'import sys; raise SystemExit("Python 3.11+ is required") if sys.version_info < (3, 11) else None'
	$(PYTHON) -m venv .venv
	.venv/bin/python -m pip install --upgrade pip
	.venv/bin/python -m pip install -r requirements.txt

run:
	.venv/bin/python -m telegram_voice_bot

check:
	.venv/bin/python -m telegram_voice_bot --check

test:
	.venv/bin/python -m unittest discover -s tests -v
