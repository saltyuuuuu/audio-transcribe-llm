from __future__ import annotations

from pathlib import Path

from .config import AppConfig
from .media import audio_duration_seconds, ensure_mp3_or_wav, format_duration, remove_tree, split_audio
from .prompts import ZH_CORRECTION_PROMPT, ZH_SUMMARY_PROMPT, choose_transcribe_prompt
from .providers import ArkMediaClient, TextLLMClient, transcribe_segments_with_fallback
from .report import build_markdown_report, export_html_pdf


async def transcribe_only(audio_path: str, language: str | None = None, config: AppConfig | None = None) -> str:
    cfg = config or AppConfig.from_env()
    prepared = ensure_mp3_or_wav(audio_path)
    tmpdir, segments = split_audio(
        prepared,
        segment_seconds=cfg.runtime.segment_seconds,
        timeout=cfg.runtime.ffmpeg_split_timeout,
    )
    try:
        raw, _stats = await transcribe_segments_with_fallback(
            ArkMediaClient(cfg.ark),
            segments,
            choose_transcribe_prompt(language),
            cfg.runtime.segment_seconds,
            cfg.runtime.max_workers,
        )
        return raw
    finally:
        remove_tree(tmpdir)


async def full_report(
    audio_path: str,
    output_dir: str | None = None,
    language: str | None = None,
    no_pdf: bool = False,
    config: AppConfig | None = None,
) -> dict[str, str | None]:
    cfg = config or AppConfig.from_env()
    source = Path(audio_path).expanduser().resolve()
    out_dir = Path(output_dir).expanduser().resolve() if output_dir else source.parent / f"转写结果_{source.stem}"
    out_dir.mkdir(parents=True, exist_ok=True)
    prepared = ensure_mp3_or_wav(source, out_dir)
    duration = format_duration(audio_duration_seconds(prepared))
    tmpdir, segments = split_audio(
        prepared,
        segment_seconds=cfg.runtime.segment_seconds,
        timeout=cfg.runtime.ffmpeg_split_timeout,
    )
    try:
        raw, stats = await transcribe_segments_with_fallback(
            ArkMediaClient(cfg.ark),
            segments,
            choose_transcribe_prompt(language),
            cfg.runtime.segment_seconds,
            cfg.runtime.max_workers,
        )
    finally:
        remove_tree(tmpdir)

    text_client = TextLLMClient(cfg.text)
    corrected = await text_client.chat(
        ZH_CORRECTION_PROMPT.format(transcript=raw),
        system_prompt="你是严谨的中文语音转写校对员。你只修正明显错误，不编造未听清内容。",
    )
    summary = await text_client.chat(
        ZH_SUMMARY_PROMPT.format(corrected=corrected),
        system_prompt="你是会议纪要和长音频摘要专家，输出结构清晰、克制、准确。",
    )

    model_line = f"{cfg.ark.lite_model} / {cfg.ark.mini_model}; text={cfg.text.model}"
    markdown = build_markdown_report(
        title=source.stem,
        model_line=model_line,
        duration=duration,
        raw_transcript=raw,
        corrected=corrected,
        summary=summary,
        source_path=str(source),
    )
    md_path = out_dir / f"转写结果_{source.stem}.md"
    md_path.write_text(markdown, encoding="utf-8")
    html_path: Path | None = None
    pdf_path: Path | None = None
    try:
        html_path, pdf_path = export_html_pdf(md_path, no_pdf=no_pdf)
    except Exception as exc:
        html_path = md_path.with_suffix(".html") if md_path.with_suffix(".html").exists() else None
        pdf_path = None
        (out_dir / "PDF_EXPORT_FAILED.txt").write_text(str(exc), encoding="utf-8")
    return {
        "markdown": str(md_path),
        "html": str(html_path) if html_path else None,
        "pdf": str(pdf_path) if pdf_path else None,
        "stats": f"{stats['ok']}/{stats['total']} segments ok",
    }

