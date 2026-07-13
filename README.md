# ImpressMem

ImpressMem is an impression-based memory management library for AI applications.

## Installation

```bash
pip install impressmem
```

## Quick Start

```python
from impressmem import Config, ImpressionManager

# Initialize configuration
config = Config(bot_name="MyBot", redis_config={
    "host": "localhost",
    "port": 6379,
    "db": 0
})

# Initialize ImpressionManager
manager = await ImpressionManager.initialize(config)

# Save an impression
await manager.save_impression(
    clue="user name",
    content="John Doe",
    category="personal info",
    labels=["user", "identity"],
    pin=False
)

# Get impressions
mixed_impressions = await manager.get_mixed_impressions()

# Build context
context = manager.context_builder.build_impressions_context(mixed_impressions)
```

## Features

- Category, label, clue-based hierarchical memory organization
- Time-based rolling memory with limits
- Pinned critical impressions
- Memory merge operations for organization
- Redis-based storage for efficiency
- Text unit-based memory limits for LLM context management
- Context building utilities

## Configuration

### Redis Configuration

```python
config = Config(
    bot_name="MyBot",
    redis_config={
        "host": "localhost",
        "port": 6379,
        "db": 0,
        "password": None  # optional
    }
)
```

### Memory Limits

Memory limits can be adjusted in the ImpressionManager class.

## API Reference

### Config

Configuration class for ImpressMem.

```python
Config(
    bot_name: str,
    redis_config: Dict[str, Any]
)
```

### ImpressionManager

Core memory management class.

- `initialize(config)` - Initialize the manager
- `save_impression(clue, content, category, labels, pin)` - Save an impression
- `get_mixed_impressions(max_text_units)` - Get mixed impressions
- `merge_categories(from_category, to_category)` - Merge categories
- `merge_labels(from_labels, to_label)` - Merge labels
- `merge_clues(from_clues, to_clue, new_content)` - Merge clues
- `close()` - Close Redis connection

## Publishing to PyPI

### Build the package

```bash
cd ImpressMem
pip install --upgrade build
python -m build
```

### Upload to PyPI

```bash
pip install --upgrade twine
twine upload dist/*
```

## License

MIT License
