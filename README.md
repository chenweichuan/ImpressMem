# ImpressMem

> **给 AI Agent 的印象式记忆系统** —— 不做向量检索，不做复杂召回漏斗，用 Redis zset + LLM 理解能力实现轻量记忆，依赖只有 `redis` 一个包。

ImpressMem 模拟人类"形成印象"的认知方式，让 AI Agent 拥有轻量、高效、可自进化的长期记忆能力。它不依赖向量数据库、不需要 embedding 模型、不需要部署额外服务，只需要一个 Redis 实例。

## 为什么选 ImpressMem？

现有的 AI 记忆方案功能强大，但往往需要向量数据库、embedding 模型、内部自动调用 LLM 做信息抽取，安装依赖多、部署复杂。

如果你只是想给 AI Agent 加一个轻量记忆，不想折腾这些基础设施，ImpressMem 就是为你准备的：

- **零向量数据库** —— 不需要 Qdrant/Chroma/Pinecone，不需要 embedding 模型
- **单依赖** —— `pip install impressmem` 只装 `redis`，没有 torch/numpy/openai 一堆东西
- **不调用 LLM** —— ImpressMem 本身是纯存储/检索工具，LLM 调用完全由你控制
- **印象式认知模型** —— 三级结构（category/label/clue）+ 时间衰减 + 自动合并冗余，模拟人类形成印象的方式
- **OpenAI function calling 原生支持** —— 3 个工具直接塞进 `tools` 参数就能用

## 架构

```
┌─────────────────────────────────────────────────────────┐
│                     AI Agent / LLM                       │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │ Save Tool   │  │ Recall Tool  │  │ Organize Tool  │  │
│  └──────┬──────┘  └──────┬───────┘  └───────┬────────┘  │
│         │                │                   │           │
│         └────────────────┼───────────────────┘           │
│                          │                               │
│              ┌───────────▼───────────┐                   │
│              │  slice_new_turn_msgs  │  ← 渐进式沉淀     │
│              └───────────┬───────────┘                   │
└──────────────────────────┼───────────────────────────────┘
                           │
                    ┌──────▼──────┐
                    │  Redis zset │  category/label/clue
                    └─────────────┘
```


## Installation

```bash
pip install impressmem
```

Requires Python 3.9+ and a running Redis instance (default: localhost:6379).

## Quick Start

```python
import asyncio
from impressmem import ImpressMemConfig, ImpressMemManager

async def main():
    config = ImpressMemConfig(
        bot_name="MyAssistant",
        redis_config={"host": "localhost", "port": 6379, "db": 0},
        # 也支持 Redis URL: {"url": "redis://:password@host:port/db"}
    )
    manager = ImpressMemManager(config)

    # 获取记忆上下文，直接塞进 LLM 的 system prompt
    memory_context = await manager.build_memory_context()
    print(memory_context)

    await manager.close()

asyncio.run(main())
```

## 实战场景

ImpressMem 在实战中有两种典型用法：

### 场景一：Agent 原生工具（主动调用）

三个 Tool 类实现了 OpenAI function calling 接口，直接作为工具注册给 Agent，让 LLM 在对话中自主决定何时保存、回忆、整理记忆：

```python
import json
from impressmem import (
    ImpressMemConfig, ImpressMemManager,
    SaveImpressionTool, RecallImpressionsTool, OrganizeImpressionsTool
)

config = ImpressMemConfig(bot_name="MyAssistant", redis_config={"host": "localhost"})
manager = ImpressMemManager(config)

# 初始化三个工具
save_tool = SaveImpressionTool(manager)
recall_tool = RecallImpressionsTool(manager)
organize_tool = OrganizeImpressionsTool(manager)

# 获取 OpenAI function calling 格式的工具定义
tools = [
    save_tool.get_definition(),
    recall_tool.get_definition(),
    organize_tool.get_definition(),
]

# 传给 LLM 的 tools 参数即可，Agent 会自主调用
# response = await openai.chat.completions.create(
#     model="gpt-4",
#     messages=messages,
#     tools=tools,
# )

# 执行工具调用时：
# full_result, summary = await save_tool.execute(json.dumps({
#     "clue": "USER-PREFERENCE-COLOR",
#     "content": "用户喜欢紫色主题",
#     "category": "UserPreference",
#     "labels": ["Color", "UI"],
# }))
```


### 场景二：渐进式被动沉淀（自动记忆）

搭配 `slice_new_turn_messages()` 方法，在每轮对话结束后自动蒸馏关键信息，实现"不需要 Agent 主动记，系统自动沉淀印象"的效果。

**个人助手实践示例**：[ai-bot-brain/impression_manager.py](https://github.com/chenweichuan/ai-bot-brain/blob/main/memory/impression_manager.py) 中的 `maintain_impressions_by_llm` 方法，在 Agent 每一次模型轮结束后触发：

```
用户消息 → LLM 回复 → 模型轮结束
    ↓
slice_new_turn_messages(full_history)  ← 切出本轮增量消息
    ↓
构建上下文（已有记忆 + 本轮消息 + Save/Organize 工具定义）
    ↓
LLM 自主判断：是否有新信息需要保存？是否有冗余记忆需要合并？
    ↓
自动调用 SaveImpressionTool / OrganizeImpressionsTool 执行沉淀
```

核心实现思路：

```python
from impressmem import slice_new_turn_messages

# 1. 每轮对话结束后，切出本轮增量消息
new_turn = slice_new_turn_messages(full_message_history)

# 2. 获取记忆维护的 system prompt（指导 LLM 分析消息、判断是否需要保存/合并）
maintain_prompt = manager.get_maintain_prompt()
# 返回 str，指导 LLM 分析新消息、判断是否需要保存印象或合并冗余

# 3. 获取记忆维护所需的工具定义（SaveImpressionTool + OrganizeImpressionsTool）
maintain_tools = manager.get_maintain_tool_definitions()
# 返回 List[Dict[str, Any]]，可直接传给 LLM 的 tools 参数

# 4. 构建请求并调用 LLM
messages_for_llm = [
    {"role": "system", "content": await manager.build_memory_context()},
    *new_turn,
    {"role": "user", "content": maintain_prompt},
]
response = await openai.chat.completions.create(
    model="doubao-seed-2.0-lite",
    messages=messages_for_llm,
    tools=maintain_tools,
)

# 5. 批量执行 LLM 返回的工具调用（自动分发到 save/organize 工具）
await manager.execute_maintain_tool_calls(response.choices[0].message.tool_calls)
# 参数: Optional[List[Dict[str, Any]]] — LLM response 中的 tool_calls 列表
# 每个 tool_call 格式: {"function": {"name": "...", "arguments": "<json_string>"}}
# 无法识别的工具名会被跳过并记录 warning，执行异常会被捕获并记录 error
```

两种模式可以同时使用：Agent 主动记重要信息 + 系统被动沉淀日常细节，形成完整的记忆体系。

## 记忆模型

ImpressMem 使用三级印象结构：

- **Category（分类）**：顶层分类，如 `UserPreference`、`Finance`、`Health`
- **Label（标签）**：具体属性标签，如 `Color`、`Diet`、`Schedule`
- **Clue（线索）**：最细粒度的记忆线索，如 `USER-PREF-COLOR`、`DIANDIAN-FEEDING`

每条印象包含：clue（唯一标识）、content（信息内容）、category、labels、pin（是否置顶）。记忆按时间衰减，置顶印象永久保留，系统自动合并冗余信息。

## Configuration

```python
ImpressMemConfig(
    bot_name: str,                    # Agent 名称，用作 Redis key 前缀
    redis_config: Dict[str, Any],     # Redis 连接配置
    categories_per_set: int = 500,    # 每轮上下文最大分类数
    labels_per_set: int = 1500,       # 每轮上下文最大标签数
    clues_per_set: int = 500,         # 每轮上下文最大线索数
    impression_text_units_per_set: int = 15000,  # 每轮上下文最大文本单元
    unpinned_emoji: str = "⚪",       # 非置顶印象标记
    pinned_emoji: str = "📌",         # 置顶印象标记
)
```

`redis_config` 支持两种格式：
- 传统参数：`{"host": "localhost", "port": 6379, "db": 0, "password": "xxx"}`
- URL 格式：`{"url": "redis://:password@host:6379/0"}`


## Core API

### ImpressMemManager

```python
manager = ImpressMemManager(config)

# 构建记忆上下文（用于 LLM system prompt）
memory_context = await manager.build_memory_context()

# 关闭连接
await manager.close()
```

### Tools

三个工具类均提供两个方法：
- `get_definition()` → 返回 OpenAI function calling 格式的 JSON schema
- `execute(json_args)` → 执行操作，返回 `(full_result, summary)` 元组

| Tool | 用途 |
|------|------|
| `SaveImpressionTool` | 保存一条新印象，自动去重更新 |
| `RecallImpressionsTool` | 按 category/labels 检索相关印象 |
| `OrganizeImpressionsTool` | 合并冗余分类/标签/线索，清理记忆结构 |

### Utility Functions

```python
from impressmem import slice_new_turn_messages

# 从完整对话历史中切出最新一轮消息
# 用于渐进式记忆沉淀
sliced = slice_new_turn_messages(messages)
```

## Examples

See the `examples/` directory:
- `context_example.py` - 构建记忆上下文
- `tools_example.py` - 使用三个工具类

## Contributing

Contributions welcome! Feel free to submit issues and pull requests.

## License

MIT License
