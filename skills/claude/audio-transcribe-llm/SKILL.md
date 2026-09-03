---
name: audio-transcribe-llm
description: 音频文件全套处理：长音频语音转文字、说话人区分、时间标记、内容修正、摘要总结、Markdown/HTML/PDF 报告导出。使用 Audio-Transcribe-LLM MCP，优先 Doubao Seed 2.0 Lite，失败分段 fallback 到 Mini，文本校对和摘要使用 DeepSeek V4 Pro 或用户配置的 OpenAI-compatible 文本模型。
---

# Audio Transcribe LLM

当用户要求转写音频、整理会议纪要、处理访谈/课堂/播客录音时，优先使用 `Audio-Transcribe-LLM` MCP。

## 核心原则

1. 一字不漏：原始转写阶段尽量保留所有语音内容、语气词和不确定标记。
2. 不编造失败分段：如果 MCP 输出 `[API错误]`、`[处理超时]` 或成功数小于总段数，不要用上下文猜测该分段内容。
3. 先音频后文本：先调用 MCP 完成音频读取，再用文本模型做修正、摘要和格式化。
4. 输出可交付文件：优先生成 Markdown、HTML 和 PDF 报告。

## 推荐工具

- `mcp__Audio-Transcribe-LLM__generate_audio_report`：完整报告。
- `mcp__Audio-Transcribe-LLM__transcribe_long_audio`：只要原始转写时使用。
- `mcp__Audio-Transcribe-LLM__analyze_media`：额外分析图片、短音频或视频时使用。

## 完整报告流程

调用：

```json
{
  "audio_path": "<用户提供的本地音频路径>",
  "output_dir": "<用户指定输出目录，可省略>",
  "language": "zh",
  "no_pdf": false
}
```

如果用户未说明语言，中文音频默认 `zh`；文件名或用户描述包含 English/英文/英语时用 `en`。

## 质量要求

- 如果工具返回报告路径，告诉用户 `.md`、`.html`、`.pdf` 的位置。
- 如果 PDF 失败但 Markdown/HTML 成功，说明 PDF 失败原因并保留已有路径。
- 如果某些分段失败，在最终回复中明确说明有失败分段，报告内已保留标记。
- 不要把 `spk0/spk1` 作为最终说话人名；尽量根据上下文整理为 `男老师`、`女学生`、`面试官`、`求职者` 等。

## 用户可用说法

```text
/audio-transcribe-llm "D:\audio\meeting.mp3"
```

或：

```text
请用 Audio-Transcribe-LLM 帮我转写这个录音并生成会议纪要：
"D:\audio\meeting.mp3"
```
