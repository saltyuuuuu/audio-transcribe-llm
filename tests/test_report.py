from audio_transcribe_llm.report import build_markdown_report, has_failed_segments


def test_failed_segment_detection():
    assert has_failed_segments("**成功**: 1/2\n\n> [API错误: timeout]")
    assert not has_failed_segments("**成功**: 2/2\n\nhello")


def test_build_report_contains_anchors():
    md = build_markdown_report(
        title="demo",
        model_line="doubao + deepseek",
        duration="1分0秒",
        raw_transcript="raw",
        corrected="corrected",
        summary="summary",
        source_path="demo.mp3",
    )
    assert '<a id="raw-transcript"></a>' in md
    assert "# 二、修正版" in md

