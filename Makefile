PYTHON ?= python
RIME_DEPLOYER ?= /Library/Input Methods/Squirrel.app/Contents/MacOS/rime_deployer
SHARED_DATA_DIR ?= /Library/Input Methods/Squirrel.app/Contents/SharedSupport
ROOT := $(CURDIR)

.PHONY: help
help:
	@printf '%s\n' '可用目标：'
	@printf '%s\n' '  make generate-wubi86-frost  从白霜词库生成五笔 86 词库'
	@printf '%s\n' '  make build                  使用 rime_deployer 编译 Rime 配置'
	@printf '%s\n' '  make pack                   直接打包为 dist/rime-wubi86-frost.zip'
	@printf '%s\n' '  make update-dicts           拉取并合并上游词库'
	@printf '%s\n' '  make update-dicts-check     预览上游词库更新会修改哪些文件'
	@printf '%s\n' '  make format                 使用 Prettier 格式化 YAML'
	@printf '%s\n' '  make format-check           预览 YAML 格式化会修改哪些文件'
	@printf '%s\n' '  make check                  编译 Python 脚本并构建 Rime 配置'

.PHONY: generate-wubi86-frost
generate-wubi86-frost:
	$(PYTHON) scripts/generate_wubi86_frost_dict.py

.PHONY: build
build: generate-wubi86-frost
	"$(RIME_DEPLOYER)" --build "$(ROOT)" "$(SHARED_DATA_DIR)" "$(ROOT)/build"

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
check: generate-wubi86-frost
	$(PYTHON) -m py_compile scripts/pack.py scripts/update_upstream_dicts.py scripts/format_yaml.py scripts/generate_wubi86_frost_dict.py
	"$(RIME_DEPLOYER)" --build "$(ROOT)" "$(SHARED_DATA_DIR)" "$(ROOT)/build"
