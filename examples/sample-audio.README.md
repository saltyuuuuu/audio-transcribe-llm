# Sample audio

This repository includes two small public-domain/CC0 sample files under `examples/audio/`:

- `examples/audio/sample_zh_mandarin_cc0.ogg`
- `examples/audio/sample_en_librivox_pd.mp3`

Recommended first test:

```bash
audio-transcribe-llm --env .env report "examples/audio/sample_zh_mandarin_cc0.ogg" --no-pdf
```

See `examples/audio/README.md` for source links, license notes, durations, and hashes. Do not commit private recordings or generated transcripts.
