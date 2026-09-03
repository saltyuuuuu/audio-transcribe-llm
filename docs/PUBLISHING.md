# 发布到 GitHub 操作清单

目标账号：`saltyuuuuu`

建议仓库名：

```text
audio-transcribe-llm
```

## 1. 发布前检查

```bash
python scripts/check_secrets.py
python -m compileall audio_transcribe_llm scripts
```

确认：

- `.env` 没有被提交。
- 没有真实 API Key。
- 没有真实音频、会议纪要或隐私转写结果。
- README 里的 GitHub 链接已替换为真实仓库。
- 教程截图已打码。

## 2. 初始化仓库

```bash
git init
git add .
git commit -m "Initial open-source release"
```

## 3. 创建 GitHub 仓库

网页方式：

1. 打开 https://github.com/new
2. Owner 选择 `saltyuuuuu`
3. Repository name 填 `audio-transcribe-llm`
4. 选择 Public
5. 不要勾选自动创建 README/LICENSE/gitignore，因为本地已经有

CLI 方式：

```bash
gh repo create saltyuuuuu/audio-transcribe-llm --public --source . --remote origin --push
```

如果不用 `gh`：

```bash
git remote add origin https://github.com/saltyuuuuu/audio-transcribe-llm.git
git branch -M main
git push -u origin main
```

## 4. Release 文案

标题：

```text
v0.1.0 - Agent-friendly long audio transcription with Doubao + DeepSeek
```

正文：

```markdown
First public release.

- Unified MCP server for long audio transcription.
- Doubao Seed 2.0 Lite first, Mini fallback.
- DeepSeek/OpenAI-compatible text model for correction and summaries.
- Claude Code, Codex, Hermes, OpenClaw templates.
- Setup wizard, docs, and competitor comparison notes.

Security note: no API keys are included. Copy `.env.example` to `.env` and use your own keys.
```

## 5. 后续路线图

- 增加真实 benchmark 数据集和 CER/WER 评分脚本。
- 增加 FunASR/Whisper 本地 fallback。
- 增加 Web UI 或 Tauri 小工具。
- 增加更多 Agent 的自动配置器。
- 增加可选 OSS/对象存储上传，支持超大音频 URL 模式。

