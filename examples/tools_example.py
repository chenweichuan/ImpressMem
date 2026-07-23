"""
ImpressMem 工具使用示例

本示例演示如何使用 ImpressMem 的内置工具。
命名约定：clue 使用大写字母加连字符；category 和 label 使用 PascalCase。

开发者指南：
1. 从 get_definition() 获取的工具定义可以直接追加到 OpenAI 兼容的 API 调用中
2. 模型输出的工具调用参数 JSON 可以直接传给工具的 execute() 方法
3. 对于渐进式记忆沉淀，可在每轮模型回复后使用 slice_new_turn_messages() 截取适合逐步沉淀的最新消息
"""
import asyncio
import json
from impressmem import ImpressMemConfig, ImpressMemManager, slice_new_turn_messages
from impressmem.tools import SaveImpressionTool, OrganizeImpressionsTool, RecallImpressionsTool


async def main():
    # 初始化配置
    config = ImpressMemConfig(
        bot_name="Bot",
        redis_config={
            "host": "localhost",
            "port": 6379,
            "db": 4
        }
    )

    # 初始化 ImpressionManager
    manager = ImpressMemManager(config)
    print("✅ ImpressionManager 已初始化")

    try:
        # 初始化工具
        save_tool = SaveImpressionTool(manager)
        organize_tool = OrganizeImpressionsTool(manager)
        recall_tool = RecallImpressionsTool(manager)
        print("✅ 工具已初始化")

        # 获取工具定义
        print("\n📋 工具定义:")
        save_def = save_tool.get_definition()
        organize_def = organize_tool.get_definition()
        recall_def = recall_tool.get_definition()
        print(f"  - {save_def['function']['name']}")
        print(f"  - {organize_def['function']['name']}")
        print(f"  - {recall_def['function']['name']}")

        # 示例 1: 使用工具保存印象
        print("\n📝 示例 1: 保存印象...")
        save_args = {
            "clue": "USER-JOHN-PREF",
            "content": "pref:hates-broccoli;fav-game:Zelda;last-upd:2024-01-15",
            "category": "UserPreferences",
            "labels": ["UserProfile", "FoodPreference", "Gaming"],
            "pin": False
        }
        full_result, summary = await save_tool.execute(json.dumps(save_args))
        print(f"  {summary}")

        # 示例 2: 保存另一个印象
        print("\n📝 示例 2: 保存另一个印象...")
        save_args2 = {
            "clue": "USER-MARY-PROF",
            "content": "prof:designer;tools:Figma,AdobeXD;experience:5y",
            "category": "UserProfiles",
            "labels": ["Occupation", "Design"],
            "pin": False
        }
        full_result, summary = await save_tool.execute(json.dumps(save_args2))
        print(f"  {summary}")

        # 示例 3: 按类别召回印象
        print("\n🔍 示例 3: 按类别召回印象...")
        recall_args = {
            "category": "UserPreferences"
        }
        full_result, summary = await recall_tool.execute(json.dumps(recall_args))
        print(f"  {summary}")
        print(f"  完整结果:\n{full_result}")

        # 示例 4: 按标签召回印象
        print("\n🔍 示例 4: 按标签召回印象...")
        recall_args2 = {
            "labels": ["Design"]
        }
        full_result, summary = await recall_tool.execute(json.dumps(recall_args2))
        print(f"  {summary}")
        print(f"  完整结果:\n{full_result}")

        # 示例 5: 使用整理工具合并类别
        print("\n🔀 示例 5: 合并类别...")
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
        print(f"  {summary}")
        print(f"  完整结果:\n{full_result}")

        # 显示当前记忆状态
        print("\n📊 当前记忆状态:")
        mixed_impressions = await manager.get_mixed_impressions()
        mixed_labels = await manager.get_mixed_labels()
        recent_categories = await manager.get_recent_categories()
        
        print(f"\n  类别: {[cat for cat, _ in recent_categories]}")
        print(f"  标签: {[lab for lab, _ in mixed_labels]}")
        print(f"  总印象数: {len(mixed_impressions)}")

        # 显示记忆上下文
        print("\n🧠 记忆上下文:")
        memory_context = await manager.build_memory_context()
        print("-" * 60)
        print(memory_context)
        print("-" * 60)

    finally:
        # 关闭连接
        await manager.close()
        print("\n👋 连接已关闭")


if __name__ == "__main__":
    asyncio.run(main())