# ImpressMem

ImpressMem is an impression-based memory management library for AI applications.

## Installation

### Basic installation (Redis only)
```bash
pip install impressmem
```

### With LLM support (OpenAI-compatible)
```bash
pip install "impressmem[llm]"
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
    
    memory_context = manager.context_builder.build_impressions_context(
        impression_categories=recent_categories,
        impression_labels=mixed_labels,
        impressions=mixed_impressions
    )
    
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
- **OpenAI-compatible LLM client**
- **Ready-to-use tool definitions for function calling**
- **Tool processors to execute LLM calls**

## Configuration

### Config
```python
Config(
    bot_name: str,
    bot_alias: str = "",
    owner_name: str = "",
    memory_model: str = "doubao-seed-2-1-turbo-260628",
    openai_api_key: str = None,
    openai_api_base: str = None,
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

# Merge
await manager.merge_categories(old, new)
await manager.merge_labels(sources, target)
await manager.merge_clues(sources, target, new_content=None)
```

### ContextBuilder
Memory context builder class.

```python
memory_context = manager.context_builder.build_impressions_context(
    impression_categories=recent_categories,
    impression_labels=mixed_labels,
    impressions=mixed_impressions
)
```

### LLMClient
OpenAI-compatible client for memory processing.

```python
from impressmem import Config, LLMClient

config = Config(
    openai_api_key="your-api-key",
    openai_api_base="https://your-api-base.com/v3",
    redis_config={...}
)

llm = LLMClient(config)

response = await llm.chat_completion(
    messages=[...],
    temperature=0.7,
    max_tokens=500
)
```

### Tool Definitions
Get OpenAI-compatible tool schemas.

```python
from impressmem import get_all_tools

tools = get_all_tools()  # List of save_impression, recall_impressions, organize_impressions
```

### ToolProcessor
Execute tool calls from LLM.

```python
from impressmem import ToolProcessor

processor = ToolProcessor(manager)

# Execute by name
full_result, summary = await processor.execute_tool(
    "save_impression",
    {"clue": "KEY", "content": "VALUE", "category": "CAT", "labels": ["LBL"]}
)
```

## Complete Tool Integration Example

```python
import asyncio
from impressmem import (
    Config,
    ImpressionManager,
    ToolProcessor,
    get_all_tools,
    LLMClient,
)

async def main():
    config = Config(...)
    manager = await ImpressionManager.initialize(config)
    processor = ToolProcessor(manager)
    llm = LLMClient(config)
    tools = get_all_tools()
    
    # 1. Get user message
    user_msg = "Remember that I hate broccoli"
    
    # 2. Call LLM with tools
    response = await llm.chat_completion(
        messages=[
            {"role": "user", "content": user_msg}
        ],
        tools=tools
    )
    
    # 3. Execute tool calls if any
    if response.choices[0].message.tool_calls:
        for tool_call in response.choices[0].message.tool_calls:
            full_result, summary = await processor.execute_tool(
                tool_call.function.name,
                tool_call.function.arguments
            )
            print(summary)
    
    await manager.close()
```

## Examples

See the `examples/` directory for more usage examples:
- `basic_usage.py` - Core memory operations
- `merge_example.py` - Merge operations
- `llm_example.py` - LLM client usage
- `tool_integration_example.py` - Complete tool integration

## Publishing to PyPI

### Build the package
```bash
pip install --upgrade build
python -m build
```

### Upload to PyPI
```bash
pip install --upgrade twine
twine upload dist/*
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License