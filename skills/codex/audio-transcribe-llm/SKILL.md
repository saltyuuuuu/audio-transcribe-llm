---
name: audio-transcribe-llm
description: Use when the user asks Codex to transcribe local audio, process meetings/interviews/classes/podcasts, generate verbatim transcripts, distinguish speakers, correct transcripts, summarize topics, or export Markdown/HTML/PDF reports through the Audio-Transcribe-LLM MCP server. The workflow uses Doubao Seed 2.0 Lite with Mini fallback for audio and DeepSeek V4 Pro or another OpenAI-compatible text model for correction and summaries.
---

# Audio Transcribe LLM

Use the `Audio-Transcribe-LLM` MCP server for local audio transcription and report generation.

## Workflow

1. Confirm the user supplied a local audio path.
2. Use `generate_audio_report` for full deliverables.
3. Use `transcribe_long_audio` only when the user asks for raw transcription.
4. Preserve failed segment markers. Never infer exact speech for segments that the audio model did not successfully process.
5. Report the generated file paths back to the user.

## Tool Selection

Prefer:

- `mcp__Audio-Transcribe-LLM__generate_audio_report`
- `mcp__Audio-Transcribe-LLM__transcribe_long_audio`
- `mcp__Audio-Transcribe-LLM__analyze_media`

## Full Report Arguments

```json
{
  "audio_path": "<absolute local audio path>",
  "output_dir": "<optional output directory>",
  "language": "zh",
  "no_pdf": false
}
```

Use `language: "en"` when the filename or user request clearly indicates English audio.

## Output Standard

The expected output directory contains:

```text
转写结果_<audio-name>.md
转写结果_<audio-name>.html
转写结果_<audio-name>.pdf
```

If PDF export fails, Markdown and HTML are still valid deliverables.

## Quality Rules

- Keep raw transcript and corrected transcript separate.
- Keep uncertainty markers when the model is not confident.
- Do not turn API failures into invented transcript text.
- Prefer descriptive speaker labels over mechanical `spk0/spk1`.
