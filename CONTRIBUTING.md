# Contributing

Thanks for helping improve Audio-Transcribe-LLM.

## Issues

- Search existing issues before opening a new one.
- Include OS, Python version, Provider, and minimal reproduction steps.
- Submit only redacted error messages.
- Never submit API keys, private audio, or sensitive transcripts.

## Pull requests

```powershell
python -m pip install -e ".[dev]"
pytest -q
python scripts/check_secrets.py
```

Keep changes focused and include test results in the pull request.
