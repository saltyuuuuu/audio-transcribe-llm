from __future__ import annotations

import asyncio
import base64
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx

from .config import ArkConfig, TextConfig
from .media import get_file_format, get_mime_type


def file_to_base64(file_path: str | Path) -> str:
    with open(file_path, "rb") as handle:
        return base64.b64encode(handle.read()).decode("utf-8")


def extract_text_from_chat_response(response: dict[str, Any]) -> str:
    chunks: list[str] = []
    for choice in response.get("choices", []):
        message = choice.get("message", {})
        content = message.get("content", "")
        if isinstance(content, str) and content:
            chunks.append(content)
        elif isinstance(content, list):
            for part in content:
                if isinstance(part, dict) and part.get("type") == "text":
                    chunks.append(str(part.get("text", "")))
    return "\n\n".join(part for part in chunks if part).strip() or json.dumps(response, ensure_ascii=False, indent=2)


@dataclass
class ArkMediaClient:
    config: ArkConfig

    def _headers(self) -> dict[str, str]:
        if not self.config.api_key:
            raise RuntimeError("ARK_API_KEY is missing. Run the setup wizard or fill .env first.")
        return {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }

    def transcribe_audio_sync(self, audio_path: str | Path, prompt: str, model: str) -> str:
        file_path = Path(audio_path)
        body = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_audio",
                            "input_audio": {
                                "data": file_to_base64(file_path),
                                "format": get_file_format(file_path),
                            },
                        },
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
            "reasoning_effort": "high",
            "temperature": 0.2,
        }
        with httpx.Client(timeout=httpx.Timeout(240.0, connect=30.0)) as client:
            response = client.post(
                f"{self.config.base_url.rstrip('/')}/chat/completions",
                headers=self._headers(),
                json=body,
            )
        if response.status_code != 200:
            raise RuntimeError(f"{model} HTTP {response.status_code}: {response.text[:1000]}")
        return extract_text_from_chat_response(response.json())

    async def transcribe_audio(self, audio_path: str | Path, prompt: str, model: str) -> str:
        return await asyncio.to_thread(self.transcribe_audio_sync, audio_path, prompt, model)

    async def analyze_media(self, media_path: str | Path, media_type: str, prompt: str, model: str | None = None) -> str:
        file_path = Path(media_path)
        actual_model = model or self.config.lite_model
        mime = get_mime_type(file_path)
        b64_data = file_to_base64(file_path)
        if media_type == "image":
            media_part = {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64_data}"}}
        elif media_type == "audio":
            media_part = {
                "type": "input_audio",
                "input_audio": {"data": b64_data, "format": get_file_format(file_path)},
            }
        elif media_type == "video":
            media_part = {"type": "video_url", "video_url": {"url": f"data:{mime};base64,{b64_data}"}}
        else:
            raise ValueError(f"Unsupported media type: {media_type}")
        body = {
            "model": actual_model,
            "messages": [{"role": "user", "content": [media_part, {"type": "text", "text": prompt}]}],
            "reasoning_effort": "high",
            "temperature": 0.2,
        }
        async with httpx.AsyncClient(timeout=httpx.Timeout(300.0, connect=30.0)) as client:
            response = await client.post(
                f"{self.config.base_url.rstrip('/')}/chat/completions",
                headers=self._headers(),
                json=body,
            )
        if response.status_code != 200:
            raise RuntimeError(f"{actual_model} HTTP {response.status_code}: {response.text[:1000]}")
        return extract_text_from_chat_response(response.json())


@dataclass
class TextLLMClient:
    config: TextConfig

    def _headers(self) -> dict[str, str]:
        if not self.config.api_key:
            raise RuntimeError("TEXT_API_KEY or DEEPSEEK_API_KEY is missing. Run the setup wizard or fill .env first.")
        return {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }

    async def chat(self, prompt: str, system_prompt: str = "You are a precise transcript editor.") -> str:
        body: dict[str, Any] = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
        }
        if "deepseek" in self.config.base_url.lower() or "deepseek" in self.config.model.lower():
            body["thinking"] = {"type": self.config.thinking}
            body["reasoning_effort"] = self.config.reasoning_effort
        async with httpx.AsyncClient(timeout=httpx.Timeout(600.0, connect=30.0)) as client:
            response = await client.post(
                f"{self.config.base_url.rstrip('/')}/chat/completions",
                headers=self._headers(),
                json=body,
            )
        if response.status_code != 200:
            raise RuntimeError(f"{self.config.model} HTTP {response.status_code}: {response.text[:1000]}")
        return extract_text_from_chat_response(response.json())


async def transcribe_segments_with_fallback(
    client: ArkMediaClient,
    segments: list[Path],
    base_prompt: str,
    segment_seconds: int,
    max_workers: int,
) -> tuple[str, dict[str, int]]:
    sem = asyncio.Semaphore(max_workers)
    results: list[tuple[bool, str, str] | None] = [None] * len(segments)
    stats = {"total": len(segments), "ok": 0, "lite": 0, "mini": 0, "failed": 0}

    async def run_one(index: int) -> None:
        segment = segments[index]
        segment_no = index + 1
        start_sec = index * segment_seconds
        start = f"{start_sec // 60:02d}:{start_sec % 60:02d}"
        prompt = f"{base_prompt}\n\n（第{segment_no}段，共{len(segments)}段，绝对时间从{start}开始。）"
        async with sem:
            lite_error: Exception | None = None
            for attempt in range(2):
                try:
                    text = await client.transcribe_audio(segment, prompt, client.config.lite_model)
                    results[index] = (True, f"## 第{segment_no}段 [{start}]\n\n{text}", "lite")
                    return
                except Exception as exc:
                    lite_error = exc
                    if attempt == 0:
                        await asyncio.sleep(2)
            print(f"[fallback] segment {segment_no}: lite failed, trying mini", file=sys.stderr, flush=True)
            mini_error: Exception | None = None
            for attempt in range(2):
                try:
                    text = await client.transcribe_audio(segment, prompt, client.config.mini_model)
                    results[index] = (
                        True,
                        f"## 第{segment_no}段 [{start}]\n\n> [降级补跑: {client.config.mini_model}]\n\n{text}",
                        "mini",
                    )
                    return
                except Exception as exc:
                    mini_error = exc
                    if attempt == 0:
                        await asyncio.sleep(2)
            results[index] = (
                False,
                f"## 第{segment_no}段 [{start}]\n\n> [API错误: lite={str(lite_error)[:200]}；mini={str(mini_error)[:200]}]",
                "failed",
            )

    await asyncio.gather(*(run_one(i) for i in range(len(segments))))
    parts: list[str] = []
    for index, item in enumerate(results):
        if item is None:
            start_sec = index * segment_seconds
            parts.append(f"## 第{index + 1}段 [{start_sec // 60:02d}:{start_sec % 60:02d}]\n\n> [处理超时]")
            stats["failed"] += 1
            continue
        ok, text, source = item
        parts.append(text)
        if ok:
            stats["ok"] += 1
            stats[source] += 1
        else:
            stats["failed"] += 1
    header = (
        "# Doubao Seed 2.0 全量语音转写\n\n"
        f"**总段数**: {stats['total']}（每段 {segment_seconds} 秒）\n"
        f"**成功**: {stats['ok']}/{stats['total']}\n"
        f"**Lite 成功**: {stats['lite']}\n"
        f"**Mini 降级补跑成功**: {stats['mini']}\n"
        f"**失败**: {stats['failed']}\n\n---\n\n"
    )
    return header + "\n\n".join(parts), stats

