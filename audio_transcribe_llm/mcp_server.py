from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from .config import AppConfig
from .media import detect_media_type
from .pipeline import full_report, transcribe_only
from .providers import ArkMediaClient


app = Server("Audio-Transcribe-LLM")


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="transcribe_long_audio",
            description="Split long local audio into segments, transcribe with Doubao Seed 2.0 Lite, and fallback to Mini per failed segment.",
            inputSchema={
                "type": "object",
                "properties": {
                    "audio_path": {"type": "string", "description": "Local audio file path."},
                    "language": {"type": "string", "enum": ["zh", "en"], "description": "Optional language hint."},
                },
                "required": ["audio_path"],
            },
        ),
        Tool(
            name="generate_audio_report",
            description="Generate a full Markdown/HTML/PDF transcription report with correction and summary.",
            inputSchema={
                "type": "object",
                "properties": {
                    "audio_path": {"type": "string", "description": "Local audio file path."},
                    "output_dir": {"type": "string", "description": "Optional output directory."},
                    "language": {"type": "string", "enum": ["zh", "en"], "description": "Optional language hint."},
                    "no_pdf": {"type": "boolean", "description": "Skip PDF export."},
                },
                "required": ["audio_path"],
            },
        ),
        Tool(
            name="analyze_media",
            description="Analyze a local image/audio/video file using Doubao Seed 2.0 Lite.",
            inputSchema={
                "type": "object",
                "properties": {
                    "media_path": {"type": "string", "description": "Local media path."},
                    "prompt": {"type": "string", "description": "Analysis prompt."},
                },
                "required": ["media_path", "prompt"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]):
    try:
        config = AppConfig.from_env()
        if name == "transcribe_long_audio":
            text = await transcribe_only(
                arguments["audio_path"],
                language=arguments.get("language"),
                config=config,
            )
            return [TextContent(type="text", text=text)]
        if name == "generate_audio_report":
            result = await full_report(
                arguments["audio_path"],
                output_dir=arguments.get("output_dir"),
                language=arguments.get("language"),
                no_pdf=bool(arguments.get("no_pdf", False)),
                config=config,
            )
            return [TextContent(type="text", text="\n".join(f"{k}: {v}" for k, v in result.items()))]
        if name == "analyze_media":
            media_path = Path(arguments["media_path"]).expanduser().resolve()
            media_type = detect_media_type(media_path)
            if media_type == "unknown":
                return [TextContent(type="text", text=f"Unsupported media type: {media_path}")]
            text = await ArkMediaClient(config.ark).analyze_media(
                media_path,
                media_type,
                arguments["prompt"],
                model=config.ark.lite_model,
            )
            return [TextContent(type="text", text=text)]
        return [TextContent(type="text", text=f"Unknown tool: {name}")]
    except Exception as exc:
        return [TextContent(type="text", text=f"ERROR: {exc}")]


async def async_main() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


def main() -> None:
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
