# Audio-Transcribe-LLM 零门槛接入教程

> 更新时间：2026-06-19。云平台入口、活动规则和模型名可能变化，发布前建议再点一次官方链接确认。

> 展示名统一为 **Audio-Transcribe-LLM**；命令行、仓库地址、目录名仍使用小写 `audio-transcribe-llm`，这样复制命令时不会出错。

## 1. 准备环境

必须安装：

- Python 3.10+
- FFmpeg（包含 `ffmpeg` 和 `ffprobe`）
- 一个火山方舟账号
- 一个 DeepSeek 开放平台账号，或任意 OpenAI-compatible 文本模型账号

检查：

```bash
python --version
ffmpeg -version
ffprobe -version
```

## 2. 获取火山方舟 API Key

官方入口：

- 火山方舟：https://console.volcengine.com/ark
- 协作奖励计划：https://www.volcengine.com/docs/82379/1391869
- 模型列表：https://www.volcengine.com/docs/82379/1330310

操作步骤：

1. 登录火山引擎，进入「火山方舟」。
2. 开通方舟服务并完成必要的实名认证/授权。
3. 进入「API Key 管理」或「密钥管理」，创建 API Key。
4. 进入「模型列表」或「模型服务」，确认你的账号可调用：
   - `doubao-seed-2-0-lite-260428`
   - `doubao-seed-2-0-mini-260428`
5. 参加「协作奖励计划」。官方规则写明：平台会采集授权接入点的模型推理数据，并在次日发放等量免费资源包；每个模型每日采集上限以官方页面为准。

> 注意：网上常说的“每天 200W tokens”通常指活动阶段/特定模型的权益口径。官方页面当前描述的是“每个模型不超过 500 万 tokens 的推理数据采集并次日返还等量资源包”。不要把它理解成永久固定额度。

把 Key 写入 `.env`：

```env
ARK_API_KEY=你的火山方舟APIKey
ARK_MODEL_ID_LITE=doubao-seed-2-0-lite-260428
ARK_MODEL_ID_MINI=doubao-seed-2-0-mini-260428
```

## 3. 获取 DeepSeek / 文本模型 API Key

官方入口：

- DeepSeek API 文档：https://api-docs.deepseek.com/
- 模型与价格：https://api-docs.deepseek.com/quick_start/pricing
- 模型列表接口：https://api-docs.deepseek.com/api/list-models

操作步骤：

1. 登录 DeepSeek 开放平台。
2. 创建 API Key。
3. 在 `.env` 中填写：

```env
TEXT_API_KEY=你的DeepSeek或兼容端点APIKey
TEXT_BASE_URL=https://api.deepseek.com
TEXT_MODEL_ID=deepseek-v4-pro
```

如果接口报“模型不存在”，运行或查看模型列表，把 `TEXT_MODEL_ID` 换成可用模型。DeepSeek 和各类代理端点的模型别名可能变化，因此开源项目不要把单个模型名写死；以官方 Models 接口、控制台或你使用的代理服务说明为准。

## 4. 最省事：把提示词发给 Agent 一键配置

如果你已经有 Codex、Claude Code、Hermes、OpenClaw 等 Agent 工具，可以不用自己手动改配置。把下面这段提示词复制给你的 Agent，然后把 `XXXXX` 换成你自己的 Key。

```text
请帮我安装并配置 Audio-Transcribe-LLM。

项目地址：
git clone https://github.com/saltyuuuuu/audio-transcribe-llm.git

我的火山方舟 API Key 是：
XXXXX

我的 DeepSeek / 其他文本模型 API Key 是：
XXXXXXX

文本模型配置如下：
TEXT_BASE_URL=https://api.deepseek.com
TEXT_MODEL_ID=deepseek-v4-pro

请你完成以下事项：
1. clone 这个项目，并进入项目目录。
2. 根据我的系统选择合适的一键安装脚本：Windows 用 scripts/setup.ps1，macOS/Linux 用 scripts/setup.sh。
3. 把我的火山方舟 API Key 写入 .env 的 ARK_API_KEY。
4. 把我的文本模型 API Key 写入 .env 的 TEXT_API_KEY。
5. 生成当前 Agent 可用的 MCP 配置，并告诉我需要复制到哪里。
6. 不要把我的 API Key 写入 README、代码、Git commit 或任何公开文件。
7. 安装完成后运行基础检查，并告诉我下一步如何试用。
```

如果你使用的不是 DeepSeek 官方接口，而是其他 OpenAI-compatible 文本模型，把提示词里的两行改掉即可：

```text
TEXT_BASE_URL=你的文本模型接口地址
TEXT_MODEL_ID=你的文本模型名
```

### 安装后试用提示词

安装完成后，把下面这段发给 Agent。仓库已经内置一个中文示例音频和一个英文示例音频，不需要用户自己先找文件：

```text
请进入 Audio-Transcribe-LLM 项目目录，并使用仓库自带的中文示例音频做一次转写和总结：
"examples/audio/sample_zh_mandarin_cc0.ogg"

要求：
1. 生成完整转写报告。
2. 输出 Markdown、HTML、PDF 三种文件。
3. 告诉我生成文件的路径。
4. 如果 PDF 导出失败，说明原因，并保留 Markdown/HTML。
5. 如果某些音频分段 API 调用失败，不要根据上下文脑补，保留失败标记。
```

想测试英文音频时，把路径换成：

```text
"examples/audio/sample_en_librivox_pd.mp3"
```

这两个示例音频只用于安装后的冒烟测试，不用于宣称识别准确率。来源和许可证见 `examples/audio/README.md`。

### 配置完成后会出现什么

如果 Agent 按提示词配置成功，你的电脑上通常会有：

| 类型 | 名称 | 作用 |
| --- | --- | --- |
| MCP server | `Audio-Transcribe-LLM` | 统一提供音频转写和报告生成能力 |
| MCP tool | `transcribe_long_audio` | 只做长音频原始转写 |
| MCP tool | `generate_audio_report` | 生成 Markdown/HTML/PDF 完整报告 |
| MCP tool | `analyze_media` | 分析本地图片、短音频或视频 |
| Skill | `audio-transcribe-llm` | 让 Claude Code/Codex 知道何时调用 MCP，以及报告质量标准 |
| Command | `/audio-transcribe-llm` | Claude Code 可选快捷命令 |
| 配置文件 | `.env` | 保存 API Key、模型 ID、并发数、分段秒数等本机私有配置 |

不同 Agent 的展示方式会略有差异。例如 Codex/Claude Code 可能显示 MCP server 名称和 tools，Hermes/OpenClaw 可能只显示 server 或配置项；但真正可调用的工具就是上面 3 个 MCP tools。

## 5. 手动一键安装

Windows：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1
```

macOS/Linux：

```bash
bash scripts/setup.sh
```

如果你不想创建虚拟环境：

```bash
python scripts/setup.py --no-venv
```

## 6. 命令行第一次 Demo

从仓库根目录运行内置中文样例：

```bash
audio-transcribe-llm --env .env report "examples/audio/sample_zh_mandarin_cc0.ogg" --no-pdf
```

也可以测试内置英文样例：

```bash
audio-transcribe-llm --env .env report "examples/audio/sample_en_librivox_pd.mp3" --no-pdf
```

如果成功，你会得到：

- `.md`：源报告
- `.html`：可分享渲染版
- `.pdf`：如果电脑安装了 Edge/Chrome，会自动生成 PDF

## 7. 常见问题

**提示找不到 ffmpeg**

安装 FFmpeg，并把 `bin` 目录加入 PATH。

**Doubao API 返回 401/403**

检查 `ARK_API_KEY` 是否填错，模型是否开通，协作奖励计划是否已授权接入点。

**文本模型报模型不存在**

把 `TEXT_MODEL_ID` 改成当前端点支持的模型，例如 DeepSeek 官方 `/models` 返回的模型名，或你代理服务支持的 `deepseek-v4-pro`。

**PDF 没生成**

HTML 和 Markdown 仍然有效。安装 Microsoft Edge/Chrome，或设置 `CHROME_PATH`/`EDGE_PATH`。
