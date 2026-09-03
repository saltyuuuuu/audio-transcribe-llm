---
name: audio-transcribe-llm
description: Generate a full audio transcription report with Audio-Transcribe-LLM MCP.
argument-hint: "<audio_path> [output_dir]"
---

请使用 `Audio-Transcribe-LLM` MCP 为下面的音频生成完整报告：

```text
$ARGUMENTS
```

要求：

1. 调用 `generate_audio_report`。
2. 优先输出 Markdown、HTML、PDF。
3. 如果存在失败分段，保留失败标记，不要编造内容。
4. 完成后告诉用户生成文件路径。
