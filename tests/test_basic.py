"""
Basic Tests for ImpressMem

Requires Redis server running on localhost:6379
Naming convention: clue uses UPPERCASE with hyphens; category and label use PascalCase.
"""
import pytest
import asyncio
from impressmem import Config, ImpressionManager


@pytest.fixture
async def manager():
    """Fixture for ImpressionManager"""
    config = Config(
        bot_name="Bot",
        redis_config={
            "host": "localhost",
            "port": 6379,
            "db": 15  # Use a high db number for testing
        }
    )
    manager = await ImpressionManager.initialize(config)
    yield manager
    await manager.close()


@pytest.mark.asyncio
async def test_save_and_retrieve_impression(manager):
    """Test saving and retrieving an impression"""
    # Save an impression
    await manager.save_impression(
        clue="TEST-CLUE-001",
        content="test:content;data:sample",
        category="TestCategory",
        labels=["TestLabel"],
        pin=False
    )

    # Retrieve impressions
    mixed = await manager.get_mixed_impressions()
    assert len(mixed) > 0

    recent = await manager.get_recent_clues()
    assert len(recent) > 0


@pytest.mark.asyncio
async def test_pin_impression(manager):
    """Test pinning an impression"""
    await manager.save_impression(
        clue="IMPORTANT-CLUE-001",
        content="critical:yes;type:secret",
        category="ImportantData",
        labels=["Important"],
        pin=True
    )

    pinned = await manager.get_pinned_clues()
    assert len(pinned) > 0


@pytest.mark.asyncio
async def test_build_context(manager):
    """Test building context"""
    await manager.save_impression(
        clue="TEST-CLUE-002",
        content="test:context;type:sample",
        category="TestCategory",
        labels=["TestLabel"],
        pin=False
    )

    context = await manager.build_context()

    assert isinstance(context, str)
    assert len(context) > 0


@pytest.mark.asyncio
async def test_merge_categories(manager):
    """Test merging categories"""
    # Save impressions in different categories
    await manager.save_impression(
        clue="MERGE-TEST-001",
        content="cat:source;data:test",
        category="SourceCategory",
        labels=["TestLabel"],
        pin=False
    )
    await manager.save_impression(
        clue="MERGE-TEST-002",
        content="cat:target;data:test",
        category="TargetCategory",
        labels=["TestLabel"],
        pin=False
    )
    
    # Merge categories
    result = await manager.merge_categories("SourceCategory", "TargetCategory")
    assert result["level"] == "category"
    assert result["from"] == "SourceCategory"
    assert result["to"] == "TargetCategory"


@pytest.mark.asyncio
async def test_merge_labels(manager):
    """Test merging labels"""
    # Save impressions with different labels
    await manager.save_impression(
        clue="LABEL-MERGE-001",
        content="label:source1;data:test",
        category="TestCategory",
        labels=["SourceLabel1"],
        pin=False
    )
    await manager.save_impression(
        clue="LABEL-MERGE-002",
        content="label:source2;data:test",
        category="TestCategory",
        labels=["SourceLabel2"],
        pin=False
    )
    
    # Merge labels
    result = await manager.merge_labels(["SourceLabel1", "SourceLabel2"], "TargetLabel")
    assert result["level"] == "label"
    assert "SourceLabel1" in result["from"]
    assert "SourceLabel2" in result["from"]
    assert result["to"] == "TargetLabel"


@pytest.mark.asyncio
async def test_merge_clues(manager):
    """Test merging clues"""
    # Save impressions with different clues
    await manager.save_impression(
        clue="CLUE-MERGE-001",
        content="clue:source1;data:test1",
        category="TestCategory",
        labels=["TestLabel"],
        pin=False
    )
    await manager.save_impression(
        clue="CLUE-MERGE-002",
        content="clue:source2;data:test2",
        category="TestCategory",
        labels=["TestLabel"],
        pin=False
    )
    
    # Merge clues
    result = await manager.merge_clues(
        ["CLUE-MERGE-001", "CLUE-MERGE-002"],
        "CLUE-MERGE-TARGET",
        new_content="clue:merged;data:test1+test2"
    )
    assert result["level"] == "clue"
    assert "CLUE-MERGE-001" in result["from"]
    assert "CLUE-MERGE-002" in result["from"]
    assert result["to"] == "CLUE-MERGE-TARGET"
    assert "merged" in result["final_content"]