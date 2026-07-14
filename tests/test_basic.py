"""
Basic Tests for ImpressMem

Requires Redis server running on localhost:6379
Naming convention: clue uses UPPERCASE with hyphens; category and label use PascalCase.
"""
import pytest
import asyncio
import json
from impressmem import Config, ImpressionManager, slice_new_turn_messages
from impressmem.tools import SaveImpressionTool, OrganizeImpressionsTool, RecallImpressionsTool


@pytest.mark.asyncio
async def test_all_features_with_single_manager():
    """Test all features using a single manager instance to detect long-running issues"""
    config = Config(
        bot_name="Bot",
        redis_config={
            "host": "localhost",
            "port": 6379,
            "db": 15  # Use a single high db number for all tests
        }
    )
    manager = await ImpressionManager.initialize(config)
    
    try:
        # ==================== Test ImpressionManager methods ====================
        
        # 1. Test save and retrieve impression
        await manager.save_impression(
            clue="TEST-CLUE-001",
            content="test:content;data:sample",
            category="TestCategory",
            labels=["TestLabel"],
            pin=False
        )
        mixed = await manager.get_mixed_impressions()
        assert len(mixed) > 0
        recent = await manager.get_recent_clues()
        assert len(recent) > 0
        
        # 2. Test pin impression
        await manager.save_impression(
            clue="IMPORTANT-CLUE-001",
            content="critical:yes;type:secret",
            category="ImportantData",
            labels=["Important"],
            pin=True
        )
        pinned = await manager.get_pinned_clues()
        assert len(pinned) > 0
        
        # 3. Test build context
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
        
        # 4. Test merge categories
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
        result = await manager.merge_categories("SourceCategory", "TargetCategory")
        assert result["level"] == "category"
        assert result["from"] == "SourceCategory"
        assert result["to"] == "TargetCategory"
        
        # 5. Test merge labels
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
        result = await manager.merge_labels(["SourceLabel1", "SourceLabel2"], "TargetLabel")
        assert result["level"] == "label"
        assert "SourceLabel1" in result["from"]
        assert "SourceLabel2" in result["from"]
        assert result["to"] == "TargetLabel"
        
        # 6. Test merge clues
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
        
        # 7. Test additional methods used in examples
        mixed_labels = await manager.get_mixed_labels()
        assert len(mixed_labels) > 0
        recent_categories = await manager.get_recent_categories()
        assert len(recent_categories) > 0
        
        # ==================== Test tool classes ====================
        
        # Initialize tools
        save_tool = SaveImpressionTool()
        organize_tool = OrganizeImpressionsTool()
        recall_tool = RecallImpressionsTool()
        
        # Test get_definition for all tools
        save_def = await save_tool.get_definition()
        organize_def = await organize_tool.get_definition()
        recall_def = await recall_tool.get_definition()
        assert "function" in save_def
        assert "name" in save_def["function"]
        assert "function" in organize_def
        assert "name" in organize_def["function"]
        assert "function" in recall_def
        assert "name" in recall_def["function"]
        
        # Test SaveImpressionTool
        save_args = {
            "clue": "TOOL-USER-JOHN-PREF",
            "content": "pref:hates-broccoli;fav-game:Zelda;last-upd:2024-01-15",
            "category": "UserPreferences",
            "labels": ["UserProfile", "FoodPreference", "Gaming"],
            "pin": False
        }
        full_result, summary = await save_tool.execute(json.dumps(save_args))
        assert full_result
        assert summary
        
        # Test SaveImpressionTool with another impression
        save_args2 = {
            "clue": "TOOL-USER-MARY-PROF",
            "content": "prof:designer;tools:Figma,AdobeXD;experience:5y",
            "category": "UserProfiles",
            "labels": ["Occupation", "Design"],
            "pin": False
        }
        full_result, summary = await save_tool.execute(json.dumps(save_args2))
        assert full_result
        assert summary
        
        # Test RecallImpressionsTool by category
        recall_args = {
            "category": "UserPreferences"
        }
        full_result, summary = await recall_tool.execute(json.dumps(recall_args))
        assert full_result
        assert summary
        
        # Test RecallImpressionsTool by labels
        recall_args2 = {
            "labels": ["Design"]
        }
        full_result, summary = await recall_tool.execute(json.dumps(recall_args2))
        assert full_result
        assert summary
        
        # Test OrganizeImpressionsTool (merge categories)
        organize_args = {
            "level": "category",
            "from_items": ["UserProfiles"],
            "to_item": "UserPreferences",
            "reason": "两个类别都包含用户相关信息，可以合并",
            "check": "确认 UserProfiles 和 UserPreferences 有重叠的标签，可以合并",
            "is_redundant": True,
            "is_confirm": True
        }
        full_result, summary = await organize_tool.execute(json.dumps(organize_args))
        assert full_result
        assert summary
        
        # ==================== Test utility functions ====================
        
        # Test slice_new_turn_messages
        messages = [
            {"role": "system", "content": "System message"},
            {"role": "user", "content": "First user message"},
            {"role": "assistant", "content": "First assistant message"},
            {"role": "user", "content": "Second user message"},
        ]
        sliced = slice_new_turn_messages(messages)
        assert isinstance(sliced, list)
        
    finally:
        await manager.close()