from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    print("+ " + " ".join(cmd))
    return subprocess.run(cmd, cwd=ROOT, check=check)


def prompt_secret(name: str, hint: str = "") -> str:
    current = os.getenv(name, "")
    suffix = f" [{hint}]" if hint else ""
    if current:
        print(f"{name} already exists in environment; keeping it.")
        return current
    value = input(f"请输入 {name}{suffix}: ").strip()
    return value


def write_env(args: argparse.Namespace) -> Path:
    env_path = ROOT / ".env"
    if env_path.exists() and not args.force:
        print(".env already exists; use --force to overwrite.")
        return env_path
    ark_key = args.ark_api_key or prompt_secret("ARK_API_KEY", "火山方舟 API Key")
    text_key = args.text_api_key or prompt_secret("TEXT_API_KEY", "DeepSeek 或兼容文本模型 API Key")
    text_base_url = args.text_base_url or input("TEXT_BASE_URL [https://api.deepseek.com]: ").strip() or "https://api.deepseek.com"
    text_model = args.text_model or input("TEXT_MODEL_ID [deepseek-v4-pro]: ").strip() or "deepseek-v4-pro"
    content = f"""ARK_API_KEY={ark_key}
ARK_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
ARK_MODEL_ID_LITE={args.ark_lite_model}
ARK_MODEL_ID_MINI={args.ark_mini_model}

TEXT_API_KEY={text_key}
TEXT_BASE_URL={text_base_url}
TEXT_MODEL_ID={text_model}
TEXT_THINKING=enabled
TEXT_REASONING_EFFORT=max

DASHSCOPE_API_KEY=
QWEN_MODEL_ID=qwen3.5-omni-flash

MEDIA_SEGMENT_SECONDS={args.segment_seconds}
MEDIA_MAX_WORKERS={args.max_workers}
MEDIA_FFMPEG_SPLIT_TIMEOUT=1800
"""
    env_path.write_text(content, encoding="utf-8")
    print(f"Wrote {env_path}")
    return env_path


def read_env_file() -> dict[str, str]:
    values: dict[str, str] = {}
    env_path = ROOT / ".env"
    if not env_path.exists():
        return values
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def install_package(args: argparse.Namespace) -> None:
    python = sys.executable
    venv_dir = ROOT / ".venv"
    if not args.no_venv:
        if not venv_dir.exists():
            run([python, "-m", "venv", str(venv_dir)])
        if platform.system() == "Windows":
            python = str(venv_dir / "Scripts" / "python.exe")
        else:
            python = str(venv_dir / "bin" / "python")
    run([python, "-m", "pip", "install", "--upgrade", "pip"])
    run([python, "-m", "pip", "install", "-e", "."])


def python_executable_for_config(args: argparse.Namespace) -> str:
    if args.no_venv:
        return sys.executable
    if platform.system() == "Windows":
        return str((ROOT / ".venv" / "Scripts" / "python.exe").resolve())
    return str((ROOT / ".venv" / "bin" / "python").resolve())


def generate_configs(args: argparse.Namespace) -> Path:
    out = ROOT / "generated-configs"
    out.mkdir(exist_ok=True)
    python = python_executable_for_config(args)
    server_module_args = ["-m", "audio_transcribe_llm.mcp_server"]
    env_values = read_env_file()
    env = {
        "ARK_API_KEY": env_values.get("ARK_API_KEY", ""),
        "ARK_BASE_URL": env_values.get("ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3"),
        "ARK_MODEL_ID_LITE": args.ark_lite_model,
        "ARK_MODEL_ID_MINI": args.ark_mini_model,
        "TEXT_API_KEY": env_values.get("TEXT_API_KEY", ""),
        "TEXT_BASE_URL": env_values.get("TEXT_BASE_URL", "https://api.deepseek.com"),
        "TEXT_MODEL_ID": env_values.get("TEXT_MODEL_ID", "deepseek-v4-pro"),
    }
    claude = {
        "mcpServers": {
            "Audio-Transcribe-LLM": {
                "type": "stdio",
                "command": python,
                "args": server_module_args,
                "env": env,
            }
        }
    }
    (out / "claude-mcp.json").write_text(json.dumps(claude, ensure_ascii=False, indent=2), encoding="utf-8")

    codex_toml = f'''[mcp_servers."Audio-Transcribe-LLM"]
type = "stdio"
command = "{python.replace("\\", "\\\\")}"
args = ["-m", "audio_transcribe_llm.mcp_server"]

[mcp_servers."Audio-Transcribe-LLM".env]
ARK_API_KEY = "${{ARK_API_KEY}}"
ARK_BASE_URL = "{env["ARK_BASE_URL"]}"
ARK_MODEL_ID_LITE = "{args.ark_lite_model}"
ARK_MODEL_ID_MINI = "{args.ark_mini_model}"
TEXT_API_KEY = "{env["TEXT_API_KEY"]}"
TEXT_BASE_URL = "{env["TEXT_BASE_URL"]}"
TEXT_MODEL_ID = "{env["TEXT_MODEL_ID"]}"
'''
    codex_toml = codex_toml.replace('ARK_API_KEY = "${ARK_API_KEY}"', f'ARK_API_KEY = "{env["ARK_API_KEY"]}"')
    (out / "codex-config-snippet.toml").write_text(codex_toml, encoding="utf-8")

    hermes = {
        "servers": [
            {
                "name": "Audio-Transcribe-LLM",
                "transport": "stdio",
                "command": python,
                "args": server_module_args,
                "env_file": str((ROOT / ".env").resolve()),
            }
        ]
    }
    (out / "hermes-openclaw-mcp.json").write_text(json.dumps(hermes, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote config templates to {out}")
    return out


def check_tools() -> None:
    for binary in ["ffmpeg", "ffprobe"]:
        if shutil.which(binary):
            print(f"OK: {binary}")
        else:
            print(f"WARNING: {binary} not found. Install FFmpeg before transcribing audio.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Setup Audio-Transcribe-LLM.")
    parser.add_argument("--ark-api-key")
    parser.add_argument("--text-api-key")
    parser.add_argument("--text-base-url")
    parser.add_argument("--text-model")
    parser.add_argument("--ark-lite-model", default="doubao-seed-2-0-lite-260428")
    parser.add_argument("--ark-mini-model", default="doubao-seed-2-0-mini-260428")
    parser.add_argument("--segment-seconds", default=60, type=int)
    parser.add_argument("--max-workers", default=5, type=int)
    parser.add_argument("--force", action="store_true", help="Overwrite .env.")
    parser.add_argument("--no-venv", action="store_true", help="Install into current Python environment.")
    parser.add_argument("--skip-install", action="store_true", help="Only write .env and config templates.")
    args = parser.parse_args(argv)
    write_env(args)
    if not args.skip_install:
        install_package(args)
    generate_configs(args)
    check_tools()
    print("\nDone. See README.md and generated-configs/ for next steps.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
