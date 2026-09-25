# 安装说明

本安装包支持 Windows 和 macOS。安装器只使用 Python 3.11+ 标准库；安装过程不需要网络、pip、OMX、tmux 或外部模型网关。模型执行仍需要 Codex 宿主正常连接并具备对应账户权限。

当前机器仅在 Windows 上做过实测。macOS 路径和命令按同一安装器逻辑保持兼容，但不是 macOS 实机验证结论。

## 前置条件

- 已安装 Python 3.11 或更新版本。
- Codex 宿主支持原生自定义代理。
- 目标模型在你的账户和当前 Codex 宿主中可用。
- 知道目标 `CODEX_HOME`。默认优先使用环境变量 `CODEX_HOME`，未设置时使用 `~/.codex`。
- 进入新版 `codex-model-router/` 包根目录后再运行安装命令。

默认模型配置只是可编辑模板，不代表这些模型已经能被你的账户调用。

## 先试运行

Windows:

```powershell
py -3 install.py --dry-run
```

macOS:

```bash
python3 install.py --dry-run
```

试运行不会写入文件，只输出 `changed_files`、`mapping_source` 和 `codex_home`。其中 `backup` 为 `null`，不会提前分配备份目录。建议每次新版本安装或更新前都先执行一次，用它查看变化文件清单。

## 安装

Windows:

```powershell
py -3 install.py
```

macOS:

```bash
python3 install.py
```

安装会执行以下动作：

- 复制 `skill/` 到 `<CODEX_HOME>/skills/codex-model-router`。
- 生成 `<CODEX_HOME>/agents/codex-router-fast.toml`。
- 生成 `<CODEX_HOME>/agents/codex-router-standard.toml`。
- 生成 `<CODEX_HOME>/agents/codex-router-deep.toml`。
- 追加或更新 `<CODEX_HOME>/AGENTS.md` 全局文件里的 `CODEX_MODEL_ROUTER` 标记块。

安装器不会修改 `config.toml`、hooks、OMX 配置或旧版 `model-router` skill，也不会删除已有旧文件。

## 自定义目标目录

如果不想使用默认 `CODEX_HOME`，可以显式指定：

Windows:

```powershell
py -3 install.py --codex-home "$env:USERPROFILE\.codex"
```

macOS:

```bash
python3 install.py --codex-home "$HOME/.codex"
```

## 自定义模型配置

复制并编辑一个 JSON 文件，例如 `my-models.json`：

```json
{
  "version": 1,
  "tiers": {
    "fast": {
      "model": "gpt-6-luna",
      "reasoning_effort": "high"
    },
    "standard": {
      "model": "gpt-6-sol",
      "reasoning_effort": "high"
    },
    "deep": {
      "model": "gpt-6-astra",
      "reasoning_effort": "high"
    }
  }
}
```

然后安装：

Windows:

```powershell
py -3 install.py --config .\my-models.json
```

macOS:

```bash
python3 install.py --config ./my-models.json
```

重复安装时，如果已经存在 `<CODEX_HOME>/skills/codex-model-router/models.json`，安装器会保留已安装的配置。已安装后的模型映射如需更改，必须显式传入 `--config`，安装器才会替换已安装配置并重新生成代理文件。

## 更新

推荐流程：

1. 进入新版 `codex-model-router/` 包根目录。
2. 运行 `--dry-run` 查看将发生的变化。
3. 确认目标路径、变化文件清单和 `<CODEX_HOME>/AGENTS.md` 标记块。
4. 去掉 `--dry-run` 执行安装。
5. 运行测试或打开新 Codex 会话检查技能是否被识别。

旧版 `model-router` 可能仍然存在，导致界面或技能列表里出现相似入口。安装器不会自动卸载旧版；如需清理，请手动检查后再删除。

## 备份

安装器在覆盖会变化的文件前，会把旧文件备份到：

```text
<CODEX_HOME>/backups/codex-model-router/<UTC随机目录>
```

备份目录用于后续人工恢复。安装器在写入失败时会尽力回滚本次已写文件；如果仍需从更早状态恢复，可以人工检查备份目录后还原。

## 手动撤销

如需撤销本包安装，可手动删除：

```text
<CODEX_HOME>/skills/codex-model-router
<CODEX_HOME>/agents/codex-router-fast.toml
<CODEX_HOME>/agents/codex-router-standard.toml
<CODEX_HOME>/agents/codex-router-deep.toml
```

然后打开 `<CODEX_HOME>/AGENTS.md` 全局文件，删除以下标记块之间的内容：

```text
<!-- CODEX_MODEL_ROUTER:START -->
...
<!-- CODEX_MODEL_ROUTER:END -->
```

不要顺手删除旧版 `model-router` 或 OMX 文件，除非你已经确认它们不再被其他会话或工作区使用。

## 验证命令

在包根目录运行：

Windows:

```powershell
py -3 -m unittest discover -s tests -v
```

macOS:

```bash
python3 -m unittest discover -s tests -v
```

如果本机 `python` 已经指向 Python 3.11+，也可以使用：

```bash
python -m unittest discover -s tests -v
```

这些验证不宣称模型实际调用成功。模型调用还需要原生自定义代理、账户权限和宿主运行时共同支持。
