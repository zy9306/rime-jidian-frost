# 五笔86·白霜词库

这是一份个人 Rime 配置，包含四份输入方案：`五笔86·白霜词库`、`五笔86·白霜混输`、`白霜拼音` 和 `白霜拼音（不调频）`。

主方案文件：`rime_wubi86_frost.schema.yaml`

主方案 ID：`rime_wubi86_frost`

本配置默认使用纯五笔 86 方案：词条来自白霜词库，单字编码参考极点五笔。另提供三码起混入白霜拼音候选的混输方案、纯白霜拼音方案和关闭自动调频的静态方案。

## 上游来源

本配置引用并修改了两个开源配置仓库的内容：

- 极点五笔 86：<https://github.com/KyleBing/rime-wubi86-jidian>
- 白霜拼音：<https://github.com/gaboolic/rime-frost>

原始词库和配置版权归对应上游项目所有。本仓库只维护个人组合、裁剪和重命名后的配置。

## 当前结构

- `default.custom.yaml`：启用 `rime_wubi86_frost`、`rime_wubi86_frost_mix`、`rime_frost` 和 `rime_frost_static`
- `rime_wubi86_frost.schema.yaml`：五笔 86 纯五笔方案，使用白霜词库生成的五笔码表
- `rime_wubi86_frost_mix.schema.yaml`：五笔 86 + 白霜拼音混输方案
- `rime_wubi86_frost.dict.yaml`：由脚本生成的白霜五笔词库
- `rime_wubi86_frost_first.dict.yaml`：一级简码优先候选覆盖词库
- `rime_wubi86_frost.missing.tsv`：生成五笔词库时跳过的无法编码词条日志
- `rime_frost.schema.yaml`：白霜拼音纯拼音方案
- `rime_frost_static.schema.yaml`：白霜拼音纯拼音方案，关闭自动调频
- `jidian_dicts/wubi86_jidian.dict.yaml`：极点五笔主码表，作为白霜五笔词库的单字编码来源
- `rime_frost.dict.yaml`：白霜拼音聚合词库
- `frost_dicts/cn_dicts/`：白霜拼音基础词库
- `frost_dicts/cn_dicts_cell/`：白霜拼音细胞词库
- `lua/rime_datetime_translator.lua`：日期、时间、星期候选
- `scripts/generate_wubi86_frost_dict.py`：从白霜词库和极点单字码表生成五笔词库
- `squirrel.custom.yaml`：鼠须管外观配置
- `weasel.custom.yaml`：小狼毫外观配置，可不用

## 五笔86·白霜词库

`rime_wubi86_frost.dict.yaml` 是生成文件，不手工维护。生成规则：

- 词条来源为 `rime_frost.dict.yaml` 当前启用的全部 `import_tables`。
- 单字编码来源为 `jidian_dicts/wubi86_jidian.dict.yaml`。
- 单字保留极点五笔简码和全码；权重优先采用白霜单字权重，缺失时使用极点权重。
- 一级简码由 `rime_wubi86_frost_first.dict.yaml` 单独维护，并通过 `import_tables` 导入主词库；生成的主词库正文不再输出一级码，避免重复词条沿用白霜权重。
- 多字词按 86 五笔规则自动取码：二字 `AaAbBaBb`，三字 `AaBaCaCb`，四字及以上 `AaBaCaZa`。
- 含有极点单字码表未覆盖字符的白霜词条会跳过，并在生成时输出缺失字统计。
- 跳过词条会记录到 `rime_wubi86_frost.missing.tsv`，字段为来源词库、词条、原白霜编码、权重和缺失字符。

纯五笔方案关闭四码唯一自动上屏，并支持 `z` 键前缀拼音反查。

## 五笔86·白霜混输

- 五笔候选来自 `rime_wubi86_frost` 生成词库。
- 拼音候选来自 `rime_frost`。
- 一码、二码只查五笔词库。
- 三码起通过 `reverse_lookup` 查询白霜拼音词库。
- 关闭四码唯一自动上屏，避免误选拼音候选。

## 引用和修改：极点五笔

来源仓库：<https://github.com/KyleBing/rime-wubi86-jidian>

引用内容：

- `jidian_dicts/wubi86_jidian.dict.yaml` 来自上游 `wubi86_jidian.dict.yaml`

本地修改：

- `jidian_dicts/wubi86_jidian.dict.yaml` 去掉了上游头部的 `import_tables`，只保留主码表本体，供生成脚本读取单字编码。
- 未保留极点混输方案、极点扩展词库入口和极点用户词库方案入口。

## 引用和修改：白霜拼音

来源仓库：<https://github.com/gaboolic/rime-frost>

引用内容：

- `frost_dicts/cn_dicts/` 来自上游 `cn_dicts/`
- `frost_dicts/cn_dicts_cell/` 来自上游 `cn_dicts_cell/`
- `rime_frost.dict.yaml` 基于上游 `rime_frost.dict.yaml`
- `rime_frost.schema.yaml` 基于上游 `rime_frost.schema.yaml` 的词库和拼写规则需求重写

本地修改：

- `rime_frost.schema.yaml` 被裁剪为轻量纯拼音方案，用于直接输入拼音。
- `rime_frost_static.schema.yaml` 复用白霜词库和拼写规则，关闭 `enable_user_dict`，用于不自动调频的纯拼音输入。
- 移除了白霜完整方案中的 Lua 功能、Emoji、英文输入、部件拆字、OpenCC 扩展、置顶候选等功能配置。
- `rime_frost.dict.yaml` 保留白霜中文词库导入，并启用了 `frost_dicts/cn_dicts/tencent`。
- `rime_frost.dict.yaml` 移除了上游正文里的大写字母、数字造词和 `V` 类 Emoji 入口词条。
- 未引用上游 `lua/`、`opencc/`、`en_dicts/`、`symbols*.yaml`、T9 方案、仓颉方案等完整白霜配套文件。

## 部署

将本目录内容放入 Rime 用户目录后重新部署。

- macOS 鼠须管：`~/Library/Rime`
- Linux ibus-rime：`~/.config/ibus/rime`
- Windows 小狼毫：`%APPDATA%\Rime`

macOS 可手动编译验证：

```bash
"/Library/Input Methods/Squirrel.app/Contents/MacOS/rime_deployer" --build "$HOME/Library/Rime" "/Library/Input Methods/Squirrel.app/Contents/SharedSupport" "$HOME/Library/Rime/build"
```

也可以使用 Makefile，构建前会自动生成 `rime_wubi86_frost.dict.yaml`：

```bash
make build
```

单独生成白霜五笔词库：

```bash
make generate-wubi86-frost
```

旧版手动编译命令也可用于只检查用户目录：

```bash
"/Library/Input Methods/Squirrel.app/Contents/MacOS/rime_deployer" --build "$HOME/Library/Rime"
```

## 打包

```bash
make pack
```

默认输出：

```text
dist/rime-wubi86-frost.zip
```

## 更新上游词典

```bash
make update-dicts
```

先预览会修改哪些文件：

```bash
make update-dicts-check
```

脚本会拉取 `rime-wubi86-jidian` 和 `rime-frost` 的最新版本，并合并本配置实际使用的词典文件。本地方案文件、Lua 脚本和外观配置不会被覆盖。

合并规则：

- 更新 `jidian_dicts/wubi86_jidian.dict.yaml`，但移除上游 `import_tables`，供生成脚本读取单字编码。
- 更新 `frost_dicts/cn_dicts/` 和 `frost_dicts/cn_dicts_cell/` 下的白霜词库。
- 更新 `rime_frost.dict.yaml` 的导入表，继续启用 `frost_dicts/cn_dicts/tencent`，并保持正文为空。

## 格式化 YAML

```bash
make format
```

先预览会格式化哪些文件：

```bash
make format-check
```

脚本会调用 Prettier 格式化 YAML 文件。对于 `.dict.yaml` 词库文件，只格式化 `---` 到 `...` 之间的 YAML 头部，`...` 后面的码表正文会原样保留。

## 说明

Rime 的 `.dict.yaml` 字典文件不是完整 YAML 文件。`---` 到 `...` 是 YAML 头部，`...` 后面是制表符分隔的码表正文。

处理词库时应只用 YAML 解析头部，正文按 TSV 读取。
