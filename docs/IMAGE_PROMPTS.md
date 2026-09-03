# 截图与生图占位说明

当前仓库没有放真实平台后台截图，因为截图可能包含账号信息、余额、API Key 或接入点 ID。建议你发布前自己补图，所有图片放到：

```text
docs/assets/screenshots/
```

## 需要补的真实截图

| 文件名 | 内容 | 注意 |
| --- | --- | --- |
| `volcengine-ark-home.png` | 火山方舟控制台首页 | 打码账号、余额、项目 ID |
| `volcengine-api-key.png` | API Key 创建页面 | 不要露出完整 Key |
| `volcengine-collaboration-plan.png` | 协作奖励计划页面 | 打码个人信息 |
| `volcengine-model-list.png` | Doubao Seed 2.0 Lite/Mini 模型列表 | 保留模型名 |
| `deepseek-api-key.png` | DeepSeek API Key 页面 | 不要露出完整 Key |
| `deepseek-models.png` | DeepSeek 模型列表或 `/models` 返回 | 保留模型名 |

## 如果用 gpt-image-2 生成示意图

本次生成项目时没有可调用的 `gpt-image-2` 图片工具，所以先放提示词。你后续可以用这些 prompt 生成不含真实隐私的教程插图。

### 火山方舟控制台示意图

```text
Use case: ui-mockup
Asset type: documentation screenshot placeholder
Primary request: Create a clean Chinese cloud-console UI mockup for "火山方舟 API Key 创建".
Style/medium: realistic but fictional web dashboard screenshot
Composition/framing: 16:9 browser window, left sidebar, main content table, primary blue "创建 API Key" button
Text (verbatim): "火山方舟", "API Key 管理", "创建 API Key", "Doubao Seed 2.0 Lite", "Doubao Seed 2.0 Mini"
Constraints: no real company account, no real key, no QR code, no personal information, no watermark.
```

### 协作奖励计划示意图

```text
Use case: infographic-diagram
Asset type: documentation illustration
Primary request: An infographic explaining a token collaboration reward workflow for a cloud AI platform.
Style/medium: clean flat documentation illustration
Composition/framing: horizontal 4-step flow
Text (verbatim): "授权接入点", "调用模型", "次日返还资源包", "继续免费转写"
Color palette: neutral white background, blue and green accents
Constraints: no real logos, no real screenshots, no claims beyond the visible generic flow.
```

### 项目架构图

```text
Use case: infographic-diagram
Asset type: GitHub README architecture visual
Primary request: Diagram showing audio file -> Agent -> MCP server -> Doubao Seed 2.0 Lite/Mini -> DeepSeek text model -> Markdown/HTML/PDF report.
Style/medium: polished technical diagram
Composition/framing: left-to-right pipeline, compact labels, simple icons
Text (verbatim): "Audio", "Agent", "MCP", "Doubao Seed 2.0", "Text LLM", "Report"
Constraints: no real product logos, no API keys, no personal data.
```

