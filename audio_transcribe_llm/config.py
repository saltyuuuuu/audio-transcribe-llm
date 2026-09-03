from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def load_dotenv(path: str | Path | None = None) -> None:
    """Small .env loader so the project has no python-dotenv dependency."""
    env_path = Path(path or ".env")
    if not env_path.is_file():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def env_int(name: str, default: int) -> int:
    try:
        return int(env(name, str(default)))
    except ValueError:
        return default


def env_float(name: str, default: float) -> float:
    try:
        return float(env(name, str(default)))
    except ValueError:
        return default


@dataclass(frozen=True)
class ArkConfig:
    api_key: str
    base_url: str = "https://ark.cn-beijing.volces.com/api/v3"
    lite_model: str = "doubao-seed-2-0-lite-260428"
    mini_model: str = "doubao-seed-2-0-mini-260428"

    @classmethod
    def from_env(cls) -> "ArkConfig":
        return cls(
            api_key=env("ARK_API_KEY"),
            base_url=env("ARK_BASE_URL", cls.base_url),
            lite_model=env("ARK_MODEL_ID_LITE", env("ARK_MODEL_ID", cls.lite_model)),
            mini_model=env("ARK_MODEL_ID_MINI", cls.mini_model),
        )


@dataclass(frozen=True)
class TextConfig:
    api_key: str
    base_url: str = "https://api.deepseek.com"
    model: str = "deepseek-v4-pro"
    thinking: str = "enabled"
    reasoning_effort: str = "max"

    @classmethod
    def from_env(cls) -> "TextConfig":
        return cls(
            api_key=env("TEXT_API_KEY", env("DEEPSEEK_API_KEY")),
            base_url=env("TEXT_BASE_URL", env("DEEPSEEK_BASE_URL", cls.base_url)),
            model=env("TEXT_MODEL_ID", env("DEEPSEEK_MODEL_ID", cls.model)),
            thinking=env("TEXT_THINKING", cls.thinking),
            reasoning_effort=env("TEXT_REASONING_EFFORT", cls.reasoning_effort),
        )


@dataclass(frozen=True)
class RuntimeConfig:
    segment_seconds: int = 60
    max_workers: int = 5
    ffmpeg_split_timeout: float = 1800.0

    @classmethod
    def from_env(cls) -> "RuntimeConfig":
        return cls(
            segment_seconds=env_int("MEDIA_SEGMENT_SECONDS", cls.segment_seconds),
            max_workers=env_int("MEDIA_MAX_WORKERS", cls.max_workers),
            ffmpeg_split_timeout=env_float("MEDIA_FFMPEG_SPLIT_TIMEOUT", cls.ffmpeg_split_timeout),
        )


@dataclass(frozen=True)
class AppConfig:
    ark: ArkConfig
    text: TextConfig
    runtime: RuntimeConfig

    @classmethod
    def from_env(cls, dotenv_path: str | Path | None = None) -> "AppConfig":
        load_dotenv(dotenv_path)
        return cls(
            ark=ArkConfig.from_env(),
            text=TextConfig.from_env(),
            runtime=RuntimeConfig.from_env(),
        )

