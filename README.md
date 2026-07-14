# ImpressMem

ImpressMem is an impression-based memory management library for AI applications.

## Installation

Requires Redis server running on localhost:6379.

```bash
pip install impressmem
```

## Quick Start

```python
import asyncio
from impressmem import ImpressMemConfig, ImpressMemManager

async def main():
    # Initialize configuration
    config = ImpressMemConfig(
        bot_name="Bot",
        redis_config={
            "host": "localhost",
            "port": 6379,
            "db": 0
        }
    )
    
    # Initialize ImpressMemManager
    manager = ImpressMemManager(config)
    
    # Build memory context - use this to get memory context for LLM
    memory_context = await manager.build_memory_context()
    
    print(memory_context)
    await manager.close()

asyncio.run(main())
```

## Features

- Category, label, clue-based hierarchical memory organization
- Time-based rolling memory with limits
- Pinned critical impressions
- Memory merge operations for organization
- Redis-based storage for efficiency
- Text unit-based memory limits for LLM context management
- **OpenAI-compatible tool definitions for function calling**

## Configuration

### ImpressMemConfig

```python
ImpressMemConfig(
    bot_name: str,
    redis_config: Dict[str, Any] = ...,
    categories_per_set: int = 500,
    labels_per_set: int = 1500,
    clues_per_set: int = 500,
    impression_text_units_per_set: int = 15000,
    unpinned_emoji: str = "⚪",
    pinned_emoji: str = "📌",
)
```

## Core API

### ImpressMemManager

```python
# Initialize
manager = ImpressMemManager(config)

# Build memory context for LLM
memory_context = await manager.build_memory_context()

# Close connection
await manager.close()
```

### Tools for Memory Operations

OpenAI-compatible tool classes for function calling.

```python
from impressmem import SaveImpressionTool, OrganizeImpressionsTool, RecallImpressionsTool

# Initialize tools with manager
save_tool = SaveImpressionTool(manager)
organize_tool = OrganizeImpressionsTool(manager)
recall_tool = RecallImpressionsTool(manager)

# Get tool definitions for OpenAI function calling
save_def = await save_tool.get_definition()
organize_def = await organize_tool.get_definition()
recall_def = await recall_tool.get_definition()

# Execute tools with JSON arguments
full_result, summary = await save_tool.execute(json.dumps(args))
```

### Utility Functions

```python
from impressmem import slice_new_turn_messages

# Slice messages for incremental memory processing
sliced = slice_new_turn_messages(messages)
```

## Examples

See the `examples/` directory for more usage examples:
- `context_example.py` - Build memory context
- `tools_example.py` - Using the tool classes

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## License

MIT License