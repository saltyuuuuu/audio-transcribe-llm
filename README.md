# Audio-Transcribe-LLM

面向 Agent 的长音频转写工具：用 Doubao Seed 2.0 Lite/Mini 做音频理解，用 DeepSeek V4 Pro 或任意 OpenAI-compatible 文本模型做校对、摘要和报告整理。

> 项目展示名统一为 **Audio-Transcribe-LLM**。为了保证复制命令可用，GitHub 仓库名、Python 包名和 CLI 命令仍使用小写 slug：`audio-transcribe-llm`。

这个项目来自 Saltyu 的 Claude Code 自用 Skill，但开源版做了几件事：

- 不内置任何 API Key，全部改为 `.env` 管理。
- 把分散的 MCP server 收敛为一个 `Audio-Transcribe-LLM` MCP server。
- 支持 Claude Code、Codex、Hermes、OpenClaw 等支持 MCP/Skill 的 Agent。
- 提供一键配置脚本、Skill 模板、命令模板、教程和竞品对比材料。

## 适合谁

- 想把会议、访谈、课程、播客等长音频交给本地 Agent 处理的人。
- 想低成本使用火山方舟等云端模型额度的人。
- 想保留自己的 Agent 工作流，而不是把音频上传到固定会议纪要 SaaS 的人。

## 快速开始

### 方式 A：让 Agent 一键配置

把下面这段提示词复制给你的 Agent 工具，例如 Codex、Claude Code、Hermes、OpenClaw：

```text
请帮我安装并配置 Audio-Transcribe-LLM。

项目地址：
git clone https://github.com/saltyuuuuu/audio-transcribe-llm.git

安全提醒：不要把 API Key 粘贴给 Agent、聊天窗口、Issue 或代码仓库。
请复制 `.env.example` 为 `.env`，只在本机终端填写 API Key。

我的火山方舟 API Key 已在本机 `.env` 中配置。
我的 DeepSeek / 其他文本模型 API Key 已在本机 `.env` 中配置。

文本模型配置：
TEXT_BASE_URL=https://api.deepseek.com
TEXT_MODEL_ID=deepseek-v4-pro

请你完成以下事项：
1. clone 项目并进入项目目录。
2. 运行项目自带的一键安装脚本。
3. 把我的 API Key 写入本机 .env，不要写进 README、代码或 Git。
4. 生成并接入当前 Agent 可用的 MCP 配置。
5. 安装完成后运行一次基础检查，并告诉我如何试用。
```

安装完成后，把下面这段发给 Agent 试用。仓库已经内置一个中文示例音频和一个英文示例音频，不需要用户自己先找文件：

```text
请进入 Audio-Transcribe-LLM 项目目录，并使用仓库自带的中文示例音频做一次转写和总结：
"examples/audio/sample_zh_mandarin_cc0.ogg"

要求：
1. 生成 Markdown、HTML、PDF 报告。
2. 如果 PDF 失败，保留 Markdown/HTML 并说明原因。
3. 如果有失败分段，不要脑补内容，保留失败标记。
4. 告诉我生成文件的路径。
```

想测试英文音频时，把路径换成：

```text
"examples/audio/sample_en_librivox_pd.mp3"
```

内置示例只用于安装后的冒烟测试，不用于宣称识别准确率。来源和许可证见 [examples/audio/README.md](examples/audio/README.md)。

### 方式 B：自己运行命令

Windows PowerShell：

```powershell
git clone https://github.com/saltyuuuuu/audio-transcribe-llm.git
cd audio-transcribe-llm
powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1
```

macOS/Linux：

```bash
git clone https://github.com/saltyuuuuu/audio-transcribe-llm.git
cd audio-transcribe-llm
bash scripts/setup.sh
```

脚本会引导你输入：

- `ARK_API_KEY`：火山方舟 API Key，用于 Doubao Seed 2.0 Lite/Mini 音频读取。
- `TEXT_API_KEY`：DeepSeek 或其他 OpenAI-compatible 文本模型 API Key。
- `TEXT_MODEL_ID`：默认 `deepseek-v4-pro`。如果你的 DeepSeek 端点不支持这个名字，改成 `/models` 返回的可用模型即可。

生成报告：

```bash
audio-transcribe-llm --env .env report "D:/audio/meeting.mp3"
```

只做原始转写：

```bash
audio-transcribe-llm --env .env transcribe "D:/audio/meeting.mp3"
```

仓库自带两个可立即试用的公开授权音频：

| 文件 | 语言 | 时长 | 用途 |
| --- | --- | ---: | --- |
| `examples/audio/sample_zh_mandarin_cc0.ogg` | 中文普通话 | 约 30 秒 | 首次安装后测试中文转写 |
| `examples/audio/sample_en_librivox_pd.mp3` | 英文 | 约 52 秒 | 首次安装后测试英文转写 |

```bash
audio-transcribe-llm --env .env report "examples/audio/sample_zh_mandarin_cc0.ogg" --no-pdf
audio-transcribe-llm --env .env report "examples/audio/sample_en_librivox_pd.mp3" --no-pdf
```

## 输出内容

默认生成：

```text
转写结果_meeting/
├── 转写结果_meeting.md
├── 转写结果_meeting.html
└── 转写结果_meeting.pdf
```

报告包含：

- 原始转写：保留模型原始输出与失败分段标记。
- 修正版：纠正同音字、术语、口误和明显 ASR 错误。
- 分段摘要：按话题整理核心内容、参与人、时间段和分析。
- PDF/HTML：便于分享、归档和打印。

## Agent 接入

安装脚本会生成：

```text
generated-configs/
├── claude-mcp.json
├── codex-config-snippet.toml
└── hermes-openclaw-mcp.json
```

`generated-configs/` 会包含你本机的私有 API Key，已被 `.gitignore` 忽略。不要把这个目录提交到 GitHub。

配置完成后，用户电脑上通常会出现：

- 1 个 MCP server：`Audio-Transcribe-LLM`
- 3 个 MCP tools：`transcribe_long_audio`、`generate_audio_report`、`analyze_media`
- 1 个可选 Skill：`audio-transcribe-llm`，用于 Claude Code 或 Codex 识别“转写音频/会议纪要”这类任务
- 1 个可选 Claude command：`/audio-transcribe-llm`
- 1 个本机 `.env`：保存 `ARK_API_KEY`、`TEXT_API_KEY`、模型名和运行参数

你也可以直接使用仓库里的模板：

- Claude Code Skill: `skills/claude/audio-transcribe-llm/SKILL.md`
- Codex Skill: `skills/codex/audio-transcribe-llm/SKILL.md`
- Claude command: `commands/audio-transcribe-llm.md`

详细配置见 [docs/AGENT_INTEGRATION.md](docs/AGENT_INTEGRATION.md)。

## 模型策略

默认优先级：

1. `doubao-seed-2-0-lite-260428`
2. `doubao-seed-2-0-mini-260428`
3. 文本校对/摘要：`deepseek-v4-pro` 或用户配置的其他文本模型

音频模型建议保持 Doubao Seed 2.0 Lite/Mini，因为多模态音频模型通常更贵；文本模型可以自由切换到 DeepSeek Flash、Kimi、GLM、Mimo 等 OpenAI-compatible 端点。

## 文档

- [零门槛教程：火山方舟 + DeepSeek 接入](docs/GETTING_STARTED.md)
- [Agent 接入指南](docs/AGENT_INTEGRATION.md)
- [模型切换速查](docs/MODEL_SWITCHING.md)
- [竞品与技术路线对比](docs/BENCHMARK_AND_COMPETITORS.md)
- [截图与生图占位说明](docs/IMAGE_PROMPTS.md)
- [发布到 GitHub 的操作清单](docs/PUBLISHING.md)
- [资料来源](docs/SOURCES.md)

## 安全提醒

本仓库永远不要提交 `.env`、API Key、私人音频原文件或隐私转写结果；`examples/audio/` 里的两个公开授权样例除外。发布前运行：

```bash
python scripts/check_secrets.py
```

## 参考来源

- 火山方舟协作奖励计划：https://www.volcengine.com/docs/82379/1391869
- 火山方舟模型列表：https://www.volcengine.com/docs/82379/1330310
- DeepSeek API 文档：https://api-docs.deepseek.com/
- DeepSeek Models & Pricing：https://api-docs.deepseek.com/quick_start/pricing
- 通义听悟：https://tingwu.aliyun.com/
- 讯飞听见：https://www.iflyrec.com/
- 飞书妙记：https://www.feishu.cn/product/minutes
- OpenAI Whisper：https://github.com/openai/whisper
- FunASR：https://github.com/modelscope/FunASR

## License

MIT
