# 极点五笔86·白霜混输

这是一份个人 Rime 配置，包含三份输入方案：`极点五笔86·白霜混输`、`白霜拼音` 和 `白霜拼音（不调频）`。

主方案文件：`rime_jidian_frost.schema.yaml`

主方案 ID：`rime_jidian_frost`

本配置把极点五笔 86 作为主输入，三码起无前缀混入白霜拼音候选；同时保留可直接切换使用的纯白霜拼音方案 `rime_frost`，以及关闭自动调频的静态方案 `rime_frost_static`。

## 上游来源

本配置引用并修改了两个开源配置仓库的内容：

- 极点五笔 86：<https://github.com/KyleBing/rime-wubi86-jidian>
- 白霜拼音：<https://github.com/gaboolic/rime-frost>

原始词库和配置版权归对应上游项目所有。本仓库只维护个人组合、裁剪和重命名后的配置。

## 当前结构

- `default.custom.yaml`：启用 `rime_jidian_frost`、`rime_frost` 和 `rime_frost_static`
- `rime_jidian_frost.schema.yaml`：极点五笔 + 白霜拼音混输方案
- `rime_frost.schema.yaml`：白霜拼音纯拼音方案，同时作为混输依赖
- `rime_frost_static.schema.yaml`：白霜拼音纯拼音方案，关闭自动调频
- `rime_jidian.dict.yaml`：五笔入口词库，聚合极点主词库、个人词库和扩展词库
- `rime_user.dict.yaml`：个人词库
- `jidian_dicts/wubi86_jidian.dict.yaml`：极点五笔主码表
- `jidian_dicts/wubi86_jidian_extra.dict.yaml`：极点五笔扩展词库
- `rime_frost.dict.yaml`：白霜拼音聚合词库
- `cn_dicts/`：白霜拼音基础词库
- `cn_dicts_cell/`：白霜拼音细胞词库
- `lua/rime_datetime_translator.lua`：日期、时间、星期候选
- `squirrel.custom.yaml`：鼠须管外观配置
- `weasel.custom.yaml`：小狼毫外观配置，可不用

## 引用和修改：极点五笔

来源仓库：<https://github.com/KyleBing/rime-wubi86-jidian>

引用内容：

- `jidian_dicts/wubi86_jidian.dict.yaml` 来自上游 `wubi86_jidian.dict.yaml`
- `jidian_dicts/wubi86_jidian_extra.dict.yaml` 来自上游 `wubi86_jidian_extra.dict.yaml`
- `rime_user.dict.yaml` 基于上游 `wubi86_jidian_user.dict.yaml`

本地修改：

- 新增根入口词库 `rime_jidian.dict.yaml`，统一导入极点主词库、个人词库和扩展词库。
- `jidian_dicts/wubi86_jidian.dict.yaml` 去掉了上游头部的 `import_tables`，只保留主码表本体，避免子目录词库重复导入。
- `rime_user.dict.yaml` 将上游 `name: wubi86_jidian_user` 改为 `name: rime_user`。
- `rime_user.dict.yaml` 增加了“白霜 8105 二码拼音同音前 15 字”词条，用于补充二码拼音候选。
- 未引用上游 `wubi86_jidian_user_hamster.dict.yaml`。
- 未引用上游 `wubi86_jidian_extra_district.dict.yaml`。

## 引用和修改：白霜拼音

来源仓库：<https://github.com/gaboolic/rime-frost>

引用内容：

- `cn_dicts/` 来自上游 `cn_dicts/`
- `cn_dicts_cell/` 来自上游 `cn_dicts_cell/`
- `rime_frost.dict.yaml` 基于上游 `rime_frost.dict.yaml`
- `rime_frost.schema.yaml` 基于上游 `rime_frost.schema.yaml` 的词库和拼写规则需求重写

本地修改：

- `rime_frost.schema.yaml` 被裁剪为轻量纯拼音方案，用于直接输入拼音，也供 `rime_jidian_frost` 反查混输。
- `rime_frost_static.schema.yaml` 复用白霜词库和拼写规则，关闭 `enable_user_dict`，用于不自动调频的纯拼音输入。
- 移除了白霜完整方案中的 Lua 功能、Emoji、英文输入、部件拆字、OpenCC 扩展、置顶候选等功能配置。
- `rime_frost.dict.yaml` 保留白霜中文词库导入，并启用了 `cn_dicts/tencent`。
- `rime_frost.dict.yaml` 移除了上游正文里的大写字母、数字造词和 `V` 类 Emoji 入口词条。
- 未引用上游 `lua/`、`opencc/`、`en_dicts/`、`symbols*.yaml`、双拼方案、T9 方案、仓颉方案等完整白霜配套文件。

## 混输行为

- 五笔候选来自 `rime_jidian`。
- 拼音候选来自 `rime_frost`。
- 一码、二码只查五笔词库。
- 三码起通过 `reverse_lookup` 查询白霜拼音词库。
- 关闭四码唯一自动上屏，避免误选拼音候选。
- 简繁切换使用 `s2hk.json`。

## 部署

将本目录内容放入 Rime 用户目录后重新部署。

- macOS 鼠须管：`~/Library/Rime`
- Linux ibus-rime：`~/.config/ibus/rime`
- Windows 小狼毫：`%APPDATA%\Rime`

macOS 可手动编译验证：

```bash
"/Library/Input Methods/Squirrel.app/Contents/MacOS/rime_deployer" --build "$HOME/Library/Rime"
```

也可以使用 Makefile：

```bash
make build
```

## 打包

```bash
make pack
```

默认输出：

```text
dist/rime-jidian-frost.zip
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

- 更新 `jidian_dicts/wubi86_jidian.dict.yaml`，但移除上游 `import_tables`，继续由 `rime_jidian.dict.yaml` 统一聚合。
- 更新 `jidian_dicts/wubi86_jidian_extra.dict.yaml`。
- 更新 `rime_user.dict.yaml` 的上游模板部分，并保留本地新增词条。
- 更新 `cn_dicts/` 和 `cn_dicts_cell/` 下的白霜词库。
- 更新 `rime_frost.dict.yaml` 的导入表，继续启用 `cn_dicts/tencent`，并保持正文为空。

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
