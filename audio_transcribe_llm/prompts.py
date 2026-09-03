ZH_TRANSCRIBE_PROMPT = """请逐字逐句转写这段音频，一字不漏。请区分不同的说话人，为每个说话人标注：
- 性别（男/女）
- 大致年龄段（儿童/青年/中年/老年）
- 根据对话内容推断其角色身份（如老师、学生、工程师等）
对于不确定的内容用[疑似:XXX]标注，完全无法听清的内容用[无法听清]标注。保留所有语气词（嗯、啊、哦等）。标注大致的分钟时间段。"""

EN_TRANSCRIBE_PROMPT = """Please transcribe this audio verbatim, word for word. Do not omit anything. Distinguish different speakers and annotate each speaker with:
- Gender (male/female)
- Approximate age range (child/youth/middle-aged/elderly)
- Role/identity inferred from conversation context (e.g., teacher, student, engineer)
Mark uncertain content with [uncertain:XXX] and completely inaudible content with [inaudible]. Preserve all filler words. Include approximate minute-level timestamps.
Observe speaker diarization carefully. When the speaker changes, start a new line with the speaker label."""

ZH_CORRECTION_PROMPT = """请对以下音频转写结果进行修正：

【原始转写】
{transcript}

【修正要求】
1. 只修正明显的识别错误、同音字、近音词、专业术语、数字、人名、地名。
2. 修复明显语病和口误，但保留说话人的表达风格。
3. 对[无法听清]和[疑似:XXX]只做谨慎推断；没有把握就保留标记。
4. 保持说话人、时间戳和对话分段清晰。
5. 不要改变原意，不要主观扩写，不要删减信息。

请输出修正后的完整对话。"""

ZH_SUMMARY_PROMPT = """请对以下修正后的对话内容进行分段摘要分析：

【修正后的对话】
{corrected}

【输出要求】
1. 按话题划分，识别每个话题的大致起止时间。
2. 每个话题包含：话题名称、时间段、参与人、核心内容、简要分析。
3. 最后给出总体总结，列出主要结论、关键要点、共识/分歧/未尽问题。
4. 全部用中文输出。"""

REPORT_FOOTER = """---

> **生成说明**
> 本报告由 **Saltyu** 开源项目 **`Audio-Transcribe-LLM`** 生成。音频理解默认使用 **Doubao-Seed-2.0-lite/mini**，文本修正与摘要默认使用 **DeepSeek V4 Pro** 或用户配置的任意 OpenAI-compatible 文本模型。
>
> 项目地址发布后请替换为你的 GitHub 仓库链接。"""


def choose_transcribe_prompt(language: str | None = None) -> str:
    if language and language.lower().startswith("en"):
        return EN_TRANSCRIBE_PROMPT
    return ZH_TRANSCRIBE_PROMPT
