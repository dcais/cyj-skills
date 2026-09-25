# codex-model-router

`codex-model-router` 是一个 Codex 技能安装包，用来指导父代理把适合拆分的本地子任务交给不同能力层级的原生 Codex 自定义代理处理。它只影响被委派的子代理，不会改变当前父会话正在使用的模型。

这个包的设计目标是可更新、可配置、可审计。默认配置提供 `fast`、`standard`、`deep` 三个层级，但这些只是初始映射，后续可以通过 `models.json` 或安装时的 `--config` 替换，不应把它理解成固定绑定某几个模型的路由器。

## 包结构

```text
codex-model-router/
|-- README.md
|-- INSTALL.md
|-- install.py
|-- skill/
|   |-- SKILL.md
|   |-- agents/
|   |   `-- openai.yaml
|   `-- models.json
`-- tests/
```

安装器会把 `skill/` 复制到：

```text
<CODEX_HOME>/skills/codex-model-router
```

并按配置生成三个原生自定义代理：

```text
<CODEX_HOME>/agents/codex-router-fast.toml
<CODEX_HOME>/agents/codex-router-standard.toml
<CODEX_HOME>/agents/codex-router-deep.toml
```

安装器还会在 `<CODEX_HOME>/AGENTS.md` 全局文件中追加或更新一个专用的 `CODEX_MODEL_ROUTER` 标记块，用于提示父代理在适合拆分的任务中加载该技能。

## 使用方式

安装后，在普通 Codex 任务里可以显式提到 `$codex-model-router`，也可以让 `AGENTS.md` 的标记块提示父代理在合适场景中使用它。

它适合：

- 窄范围查找、提取、机械验证等可以快速核对的任务。
- 普通实现、调试、测试、代码审查等有明确交付物的任务。
- 跨文件推理、架构取舍、复杂故障定位等需要更强推理的任务。

它不会：

- 改变父会话的模型。
- 保证宿主一定会自动切换模型。
- 在没有并行收益时强行委派子代理。
- 绕过账户权限、模型不可用、工具策略或用户批准要求。
- 让安装过程依赖 OMX、tmux、hooks、pip 包或网络连接。模型执行仍需要 Codex 宿主正常连接并具备对应账户权限。

升级只在同一任务片段内最多向上升级两次。权限不足、模型不可用、凭据缺失、需求不清等属于运行环境或任务边界问题，不通过换更强模型绕过。

## 配置格式

默认 `skill/models.json` 使用 version 1 格式：

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
      "reasoning_effort": "medium"
    }
  }
}
```

这些默认值只是初始配置，不证明当前账户或当前 Codex 宿主已经具备这些模型的调用权限。可以复制该 JSON 后改成你可用的模型，再用 `--config` 安装。已安装后的模型映射如需更改，也必须通过 `--config` 重新安装并重生成角色文件。

## 验证

在包根目录运行：

```powershell
python -m unittest discover -s tests -v
```

如果 Windows 上 `python` 不指向 Python 3.11+，可以改用：

```powershell
py -3 -m unittest discover -s tests -v
```

macOS 上通常可以使用：

```bash
python3 -m unittest discover -s tests -v
```

测试通过只能说明安装器和包文件结构符合预期，不代表模型实际调用已经成功。实际模型可用性取决于 Codex 宿主、自定义代理支持和账户权限。
