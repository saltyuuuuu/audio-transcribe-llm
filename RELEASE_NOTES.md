# Audio-Transcribe-LLM v0.1.0-beta.1

This is the first public Beta release of Audio-Transcribe-LLM.

## Included

- Agent-friendly long-audio transcription
- Doubao Seed 2.0 Lite/Mini Provider
- OpenAI-compatible text model correction, summaries, and reports
- CLI and unified MCP Server
- Claude Code, Codex, Hermes, and OpenClaw templates
- Markdown, HTML, and PDF reports
- FFmpeg conversion and long-audio splitting
- Failure markers, basic CI, tests, and secret scanning

## Verified

On a fixed 20-file LibriSpeech test-clean subset: Doubao Seed 2.0 Lite WER 2.03%; Faster-Whisper tiny.en WER 4.29%. See `Benchmark测评/结果文档.md` for details.

## Beta limitations

- Users must configure third-party API keys; cloud APIs may incur cost or quota limits.
- Chinese, meetings, speaker separation, and very long audio remain under validation.
- Provider output may differ; production stability is not guaranteed.

## Security

Configure API keys only in local `.env`; never paste them into an Agent, commit them, or put them in an issue.
