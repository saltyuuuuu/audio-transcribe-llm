from __future__ import annotations

import argparse
import asyncio
import json

from .config import AppConfig
from .pipeline import full_report, transcribe_only


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Audio Transcribe LLM CLI")
    parser.add_argument("--env", default=".env", help="Path to .env file.")
    sub = parser.add_subparsers(dest="command", required=True)

    t = sub.add_parser("transcribe", help="Transcribe audio only.")
    t.add_argument("audio_path")
    t.add_argument("--language", choices=["zh", "en"], default=None)

    r = sub.add_parser("report", help="Generate Markdown/HTML/PDF report.")
    r.add_argument("audio_path")
    r.add_argument("--output-dir")
    r.add_argument("--language", choices=["zh", "en"], default=None)
    r.add_argument("--no-pdf", action="store_true")
    return parser


async def async_main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    config = AppConfig.from_env(args.env)
    if args.command == "transcribe":
        print(await transcribe_only(args.audio_path, language=args.language, config=config))
        return 0
    if args.command == "report":
        result = await full_report(
            args.audio_path,
            output_dir=args.output_dir,
            language=args.language,
            no_pdf=args.no_pdf,
            config=config,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    parser.error("unknown command")
    return 2


def main(argv: list[str] | None = None) -> int:
    return asyncio.run(async_main(argv))


if __name__ == "__main__":
    raise SystemExit(main())

