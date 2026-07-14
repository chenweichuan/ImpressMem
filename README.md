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
from impressmem import Config, ImpressionManager

async def main():
    # Initialize configuration
    config = Config(
        bot_name="Bot",
        redis_config={
            "host": "localhost",
            "port": 6379,
            "db": 0
        }
    )
    
    # Initialize ImpressionManager
    manager = await ImpressionManager.initialize(config)
    
    # Save an impression
    await manager.save_impression(
        clue="USER-NAME",
        content="John Doe",
        category="PersonalInfo",
        labels=["UserProfile", "Identity"],
        pin=False
    )
    
    # Get and build memory context
    mixed_impressions = await manager.get_mixed_impressions()
    mixed_labels = await manager.get_mixed_labels()
    recent_categories = await manager.get_recent_categories()
    
    memory_context = await manager.build_context()
    
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

### Config
```python
Config(
    bot_name: str,
    redis_config: Dict[str, Any] = ...
)
```

### Memory Limits
Memory limits can be adjusted through the ImpressionManager class constants:
- `CATEGORIES_PER_SET`: Maximum categories to keep (default: 500)
- `LABELS_PER_SET`: Maximum labels to keep (default: 1500)
- `CLUES_PER_SET`: Maximum clues to keep (default: 500)
- `IMPRESSION_TEXT_UNITS_PER_SET`: Maximum text units for impressions (default: 15000)

## API Reference

### ImpressionManager
Core memory management class.

```python
# Initialize
manager = await ImpressionManager.initialize(config)

# Save
await manager.save_impression(clue, content, category, labels, pin=False)

# Get
mixed_impressions = await manager.get_mixed_impressions()
mixed_labels = await manager.get_mixed_labels()
recent_categories = await manager.get_recent_categories()
recent_labels = await manager.get_recent_labels()
recent_clues = await manager.get_recent_clues()
pinned_clues = await manager.get_pinned_clues()
category_labels = await manager.get_category_labels(category)
category_clues = await manager.get_category_clues(category)
label_clues = await manager.get_label_clues(label)
impressions = await manager.get_impressions_by_clues(clues)

# Build context
memory_context = await manager.build_context()

# Merge
await manager.merge_categories(old, new)
await manager.merge_labels(sources, target)
await manager.merge_clues(sources, target, new_content=None)

# Close
await manager.close()
```

### Tools
OpenAI-compatible tool classes for function calling.

```python
from impressmem import SaveImpressionTool, OrganizeImpressionsTool, RecallImpressionsTool

# Initialize tools
save_tool = SaveImpressionTool()
organize_tool = OrganizeImpressionsTool()
recall_tool = RecallImpressionsTool()

# Get tool definitions (for OpenAI function calling)
save_def = await save_tool.get_definition()
organize_def = await organize_tool.get_definition()
recall_def = await recall_tool.get_definition()

# Execute tools
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

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License