# 模型切换速查

## 音频模型

默认推荐不要改：

```env
ARK_MODEL_ID_LITE=doubao-seed-2-0-lite-260428
ARK_MODEL_ID_MINI=doubao-seed-2-0-mini-260428
```

原因：

- 多模态音频模型普遍比纯文本模型贵。
- Doubao Seed 2.0 Lite/Mini 在火山方舟活动/资源包场景下成本更友好。
- 本项目的长音频切分、并发、失败分段 fallback 都围绕这两个模型优化。

如果官方模型 ID 变更，以火山方舟模型列表为准。

## 文本模型

文本模型最适合用户自由切换，因为它只处理转写后的文字：

```env
TEXT_API_KEY=你的Key
TEXT_BASE_URL=https://api.deepseek.com
TEXT_MODEL_ID=deepseek-v4-pro
```

可替换为任何 OpenAI-compatible 端点：

```env
TEXT_BASE_URL=https://api.deepseek.com
TEXT_MODEL_ID=deepseek-v4-flash
```

```env
TEXT_BASE_URL=https://open.bigmodel.cn/api/paas/v4
TEXT_MODEL_ID=glm-4.5
```

```env
TEXT_BASE_URL=https://api.moonshot.cn/v1
TEXT_MODEL_ID=kimi-k2
```

如果端点不支持 `deepseek-v4-pro`，调用模型列表接口或查看平台控制台，把 `TEXT_MODEL_ID` 改成可用模型。

## 调参建议

长会议：

```env
MEDIA_SEGMENT_SECONDS=60
MEDIA_MAX_WORKERS=5
```

容易限流：

```env
MEDIA_SEGMENT_SECONDS=60
MEDIA_MAX_WORKERS=2
```

更关注上下文连续：

```env
MEDIA_SEGMENT_SECONDS=90
MEDIA_MAX_WORKERS=3
```

注意：分段越长，单段 API payload 越大；并行越高，越容易触发限流。

