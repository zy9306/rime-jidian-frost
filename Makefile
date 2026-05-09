PYTHON ?= python
RIME_DEPLOYER ?= /Library/Input Methods/Squirrel.app/Contents/MacOS/rime_deployer
ROOT := $(CURDIR)

.PHONY: help
help:
	@printf '%s\n' 'Targets:'
	@printf '%s\n' '  make build              Build Rime config with rime_deployer'
	@printf '%s\n' '  make pack               Create dist/rime-jidian-frost.zip'
	@printf '%s\n' '  make update-dicts       Fetch and merge upstream dictionaries'
	@printf '%s\n' '  make update-dicts-check Preview upstream dictionary changes'
	@printf '%s\n' '  make format             Format YAML with Prettier'
	@printf '%s\n' '  make format-check       Preview YAML formatting changes'
	@printf '%s\n' '  make check              Compile Python scripts and build Rime config'

.PHONY: build
build:
	"$(RIME_DEPLOYER)" --build "$(ROOT)"

.PHONY: pack
pack:
	$(PYTHON) scripts/pack.py

.PHONY: update-dicts
update-dicts:
	$(PYTHON) scripts/update_upstream_dicts.py

.PHONY: update-dicts-check
update-dicts-check:
	$(PYTHON) scripts/update_upstream_dicts.py --dry-run

.PHONY: format
format:
	$(PYTHON) scripts/format_yaml.py

.PHONY: format-check
format-check:
	$(PYTHON) scripts/format_yaml.py --dry-run

.PHONY: check
check:
	$(PYTHON) -m py_compile scripts/pack.py scripts/update_upstream_dicts.py scripts/format_yaml.py
	"$(RIME_DEPLOYER)" --build "$(ROOT)"
