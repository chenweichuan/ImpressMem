# ImpressMem

> **Impression-style memory for AI Agents** — No vector search, no complex recall pipelines. Built on Redis sorted sets + LLM comprehension. The only dependency is `redis`.

ImpressMem simulates how humans form impressions, giving AI Agents lightweight, efficient, self-evolving long-term memory. No vector database, no embedding models, no extra services to deploy — just a Redis instance.

## Why ImpressMem?

Existing AI memory solutions are powerful, but they typically require vector databases, embedding models, and internal LLM calls for information extraction — heavy dependencies and complex deployment.

If you just want to add lightweight memory to your AI Agent without all that infrastructure, ImpressMem is for you:

- **Zero vector database** — No Qdrant/Chroma/Pinecone needed, no embedding models required
- **Single dependency** — `pip install impressmem` installs only `redis`, no torch/numpy/openai bloat
- **No LLM calls built-in** — ImpressMem is a pure storage/retrieval utility; you control all LLM calls
- **Impression-based cognitive model** — Three-level structure (category/label/clue) + time decay + automatic deduplication, mimicking how humans form impressions
- **Native OpenAI function calling support** — Drop 3 tools into the `tools` parameter and you're done

## Architecture

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
│              │ slice_new_turn_msgs   │  ← passive sink   │
│              └───────────┬───────────┘                   │
└──────────────────────────┼───────────────────────────────┘
                           │
                    ┌──────▼──────┐
                    │ Redis zset  │  category/label/clue
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
        # Redis URL also supported: {"url": "redis://:password@host:port/db"}
    )
    manager = ImpressMemManager(config)

    # Build memory context, inject directly into LLM system prompt
    memory_context = await manager.build_memory_context()
    print(memory_context)

    await manager.close()

asyncio.run(main())
```

## Usage Patterns

ImpressMem has two typical usage patterns in practice:

### Pattern 1: Agent-Native Tools (Active Recall)

Three Tool classes implement the OpenAI function calling interface. Register them as tools for your Agent, and the LLM autonomously decides when to save, recall, or organize memories during conversation:

```python
import json
from impressmem import (
    ImpressMemConfig, ImpressMemManager,
    SaveImpressionTool, RecallImpressionsTool, OrganizeImpressionsTool
)

config = ImpressMemConfig(bot_name="MyAssistant", redis_config={"host": "localhost"})
manager = ImpressMemManager(config)

# Initialize tools
save_tool = SaveImpressionTool(manager)
recall_tool = RecallImpressionsTool(manager)
organize_tool = OrganizeImpressionsTool(manager)

# Get OpenAI function calling tool definitions
tools = [
    save_tool.get_definition(),
    recall_tool.get_definition(),
    organize_tool.get_definition(),
]

# Pass to LLM tools parameter; Agent calls them autonomously
# response = await openai.chat.completions.create(
#     model="gpt-4",
#     messages=messages,
#     tools=tools,
# )

# Execute tool calls:
# full_result, summary = await save_tool.execute(json.dumps({
#     "clue": "USER-PREFERENCE-COLOR",
#     "content": "User prefers purple theme",
#     "category": "UserPreference",
#     "labels": ["Color", "UI"],
# }))
```


### Pattern 2: Passive Progressive Sink (Automatic Memory)

Use `slice_new_turn_messages()` to automatically distill key information after each conversation turn, achieving "memory without the Agent explicitly saving" — the system passively forms impressions.

**Personal assistant example**: The `maintain_impressions_by_llm` method in [ai-bot-brain/impression_manager.py](https://github.com/chenweichuan/ai-bot-brain/blob/main/memory/impression_manager.py) triggers after every model turn:

```
User message → LLM reply → model turn ends
    ↓
slice_new_turn_messages(full_history)  ← extract incremental messages
    ↓
Build context (existing memories + new turn + Save/Organize tool defs)
    ↓
LLM autonomously decides: new info to save? redundant memories to merge?
    ↓
Auto-invoke SaveImpressionTool / OrganizeImpressionsTool to sink
```

Core implementation:

```python
from impressmem import slice_new_turn_messages

# 1. After each turn, slice out the incremental messages
new_turn = slice_new_turn_messages(full_message_history)

# 2. Get the system prompt for memory maintenance (guides LLM to analyze messages, decide whether to save/merge)
maintain_prompt = manager.get_maintain_prompt()
# Returns str, instructing the LLM to analyze new messages, decide whether to save impressions or merge redundant ones

# 3. Get tool definitions for memory maintenance (SaveImpressionTool + OrganizeImpressionsTool)
maintain_tools = manager.get_maintain_tool_definitions()
# Returns List[Dict[str, Any]], ready to pass to the LLM tools parameter

# 4. Build the request and call the LLM
messages_for_llm = [
    {"role": "system", "content": await manager.build_memory_context()},
    *new_turn,
    {"role": "user", "content": maintain_prompt},
]
response = await openai.chat.completions.create(
    model="gpt-4",
    messages=messages_for_llm,
    tools=maintain_tools,
)

# 5. Batch-execute tool calls returned by the LLM (auto-dispatches to save/organize tools)
await manager.execute_maintain_tool_calls(response.choices[0].message.tool_calls)
# Args: Optional[List[Dict[str, Any]]] — the tool_calls list from the LLM response
# Each tool_call format: {"function": {"name": "...", "arguments": "<json_string>"}}
# Unrecognized tool names are skipped with a warning; execution errors are caught and logged
```

Both patterns can be used together: the Agent actively saves important info + the system passively sinks daily details, forming a complete memory system.


## Memory Model

ImpressMem uses a three-level impression structure:

- **Category**: Top-level classification, e.g. `UserPreference`, `Finance`, `Health`
- **Label**: Specific attribute tags, e.g. `Color`, `Diet`, `Schedule`
- **Clue**: Finest-grained memory cue, e.g. `USER-PREF-COLOR`, `DIANDIAN-FEEDING`

Each impression contains: clue (unique ID), content (information), category, labels, pin (whether pinned). Memories decay over time; pinned impressions persist permanently; the system automatically merges redundant entries.

## Configuration

```python
ImpressMemConfig(
    bot_name: str,                    # Agent name, used as Redis key prefix
    redis_config: Dict[str, Any],     # Redis connection config
    categories_per_set: int = 500,    # Max categories per context
    labels_per_set: int = 1500,       # Max labels per context
    clues_per_set: int = 500,         # Max clues per context
    impression_text_units_per_set: int = 15000,  # Max text units per context
    unpinned_emoji: str = "⚪",       # Unpinned impression marker
    pinned_emoji: str = "📌",         # Pinned impression marker
)
```

`redis_config` supports two formats:
- Traditional: `{"host": "localhost", "port": 6379, "db": 0, "password": "xxx"}`
- URL format: `{"url": "redis://:password@host:6379/0"}`

## Core API

### ImpressMemManager

```python
manager = ImpressMemManager(config)

# Build memory context (for LLM system prompt)
memory_context = await manager.build_memory_context()

# Close connection
await manager.close()
```

### Tools

All three tool classes provide two methods:
- `get_definition()` → Returns OpenAI function calling JSON schema
- `execute(json_args)` → Executes the operation, returns `(full_result, summary)` tuple

| Tool | Purpose |
|------|---------|
| `SaveImpressionTool` | Save a new impression, auto-deduplicate and update |
| `RecallImpressionsTool` | Retrieve impressions by category/labels |
| `OrganizeImpressionsTool` | Merge redundant categories/labels/clues, clean up memory |

### Utility Functions

```python
from impressmem import slice_new_turn_messages

# Slice out the latest turn from full conversation history
# Used for progressive memory sinking
sliced = slice_new_turn_messages(messages)
```

## Examples

See the `examples/` directory:
- `context_example.py` - Building memory context
- `tools_example.py` - Using the three tool classes

## Contributing

Contributions welcome! Feel free to submit issues and pull requests.

## License

MIT License