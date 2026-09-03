# Built-in sample audio

This directory contains two small, redistributable audio files for first-run smoke tests. They are meant to prove that the installation, API keys, audio splitting, transcription, and report generation path works. They are not a benchmark dataset and should not be used to claim model accuracy.

| File | Language | Duration | Size | Source | License |
| --- | --- | ---: | ---: | --- | --- |
| `sample_zh_mandarin_cc0.ogg` | Chinese / Mandarin | 29.94 s | 269 KB | Wikimedia Commons, `File:无盐村.ogg` | Public domain / CC0 metadata on Commons |
| `sample_en_librivox_pd.mp3` | English | 52.14 s | 408 KB | Internet Archive / LibriVox, `A Noiseless Patient Spider by Walt Whitman`, reader `wedschild` | Public Domain |

SHA256 checksums:

```text
sample_zh_mandarin_cc0.ogg  cbb77ce52ba938abd1cff6dbc7e04082bb708624da3f2085fb627fed94986679
sample_en_librivox_pd.mp3   596e3e8c961859e5c92190a7d6a7f02c90e297679547562f943d65ebb1937ebe
```

Source links:

- Chinese sample page: https://commons.wikimedia.org/wiki/File:%E6%97%A0%E7%9B%90%E6%9D%91.ogg
- Chinese direct media URL: https://upload.wikimedia.org/wikipedia/commons/8/80/%E6%97%A0%E7%9B%90%E6%9D%91.ogg
- English sample page: https://archive.org/details/patient_spider
- English direct media URL: https://archive.org/download/patient_spider/patient_spider_witman_kr_64kb.mp3

Quick test from the repository root:

```bash
audio-transcribe-llm --env .env report "examples/audio/sample_zh_mandarin_cc0.ogg" --no-pdf
audio-transcribe-llm --env .env report "examples/audio/sample_en_librivox_pd.mp3" --no-pdf
```

Do not commit private recordings or generated transcripts. The root `.gitignore` ignores normal audio files by default and only allows these two curated sample files under `examples/audio/`.
