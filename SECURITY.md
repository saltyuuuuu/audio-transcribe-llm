# Security Policy

## Never commit secrets

Do not commit:

- `.env`
- API keys
- cloud access keys
- private audio/video files
- generated transcripts from private meetings
- screenshots that reveal account IDs, balances, request logs, or API keys

Run before every public release:

```bash
python scripts/check_secrets.py
```

## If a key was committed

1. Revoke the key in the provider console immediately.
2. Create a new key.
3. Remove the key from Git history before pushing, or rotate again after force-cleaning.
4. Do not rely on deleting one commit from GitHub UI; assume exposed keys are compromised.

## Responsible disclosure

If you find a security issue, open a private advisory on GitHub or contact the maintainer through the GitHub profile.

