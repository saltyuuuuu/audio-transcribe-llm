# Audio-Transcribe-LLM Agent 接入指南

## MCP server

开源版提供一个统一 MCP server：

```bash
python -m audio_transcribe_llm.mcp_server
```

工具：

- `transcribe_long_audio`
- `generate_audio_report`
- `analyze_media`

配置完成后的可见项通常是：

| 类型 | 名称 | 说明 |
| --- | --- | --- |
| MCP server | `Audio-Transcribe-LLM` | 统一 server 名称 |
| MCP tool | `transcribe_long_audio` | 长音频原始转写 |
| MCP tool | `generate_audio_report` | 生成完整报告 |
| MCP tool | `analyze_media` | 媒体分析 |
| Skill | `audio-transcribe-llm` | 可选，安装到 Claude/Codex skills 目录 |
| Command | `/audio-transcribe-llm` | 可选，Claude Code 快捷命令 |

Skill 和 Command 是“引导 Agent 怎么用工具”的模板；真正执行 API 调用的是 MCP server。

## Claude Code

把 `generated-configs/claude-mcp.json` 合并到 `~/.claude/mcp.json`。

注意：`generated-configs/` 是本机私有配置，里面可能包含 API Key，已被 `.gitignore` 忽略，不要提交。

或者手动添加：

```json
{
  "mcpServers": {
    "Audio-Transcribe-LLM": {
      "type": "stdio",
      "command": "C:/path/to/audio-transcribe-llm/.venv/Scripts/python.exe",
      "args": ["-m", "audio_transcribe_llm.mcp_server"],
      "env": {
        "ARK_API_KEY": "你的Key，推荐改为从本机环境变量注入",
        "TEXT_API_KEY": "你的Key，推荐改为从本机环境变量注入",
        "TEXT_BASE_URL": "https://api.deepseek.com",
        "TEXT_MODEL_ID": "deepseek-v4-pro"
      }
    }
  }
}
```

Skill 放置：

```text
~/.claude/skills/audio-transcribe-llm/SKILL.md
```

模板位置：

```text
skills/claude/audio-transcribe-llm/SKILL.md
```

## Codex

把 `generated-configs/codex-config-snippet.toml` 合并到 `~/.codex/config.toml`：

```toml
[mcp_servers."Audio-Transcribe-LLM"]
type = "stdio"
command = "C:\\path\\to\\audio-transcribe-llm\\.venv\\Scripts\\python.exe"
args = ["-m", "audio_transcribe_llm.mcp_server"]

[mcp_servers."Audio-Transcribe-LLM".env]
ARK_API_KEY = "${ARK_API_KEY}"
TEXT_API_KEY = "${TEXT_API_KEY}"
TEXT_BASE_URL = "https://api.deepseek.com"
TEXT_MODEL_ID = "deepseek-v4-pro"
```

Codex Skill 放置：

```text
~/.codex/skills/audio-transcribe-llm/SKILL.md
```

模板位置：

```text
skills/codex/audio-transcribe-llm/SKILL.md
```

## Hermes / OpenClaw / 其他 Agent

只要支持 MCP stdio，就按同一模式配置：

```json
{
  "servers": [
    {
      "name": "Audio-Transcribe-LLM",
      "transport": "stdio",
      "command": "python",
      "args": ["-m", "audio_transcribe_llm.mcp_server"],
      "env_file": "/path/to/audio-transcribe-llm/.env"
    }
  ]
}
```

如果某个 Agent 不支持 `env_file`，就把 `.env` 里的变量转成它支持的 `env` 字段。

## 推荐提示词

```text
请进入 Audio-Transcribe-LLM 项目目录，并使用仓库自带的中文示例音频生成完整转写报告：
"examples/audio/sample_zh_mandarin_cc0.ogg"

要求：
1. 一字不漏转写。
2. 保留失败分段标记，不要编造。
3. 输出 Markdown、HTML、PDF。
4. 告诉我生成文件的路径。
```

仓库还自带一个英文示例音频：`examples/audio/sample_en_librivox_pd.mp3`。这两个文件只用于安装后的冒烟测试；处理真实会议或课程时，把路径换成用户电脑上的真实音频文件。

## 为什么同时放 Skill 和 MCP

MCP server 负责确定性工具能力：切分音频、调用 API、生成文件。

Skill 负责告诉 Agent 什么时候、按什么质量标准调用工具：一字不漏、失败分段不脑补、说话人命名、报告格式等。
