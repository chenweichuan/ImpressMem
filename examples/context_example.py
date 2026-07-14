"""
ImpressMem 上下文构建示例

本示例演示如何使用 ImpressMem 构建记忆上下文。
对于开发者来说，只需将上下文和工具使用集成到自己的 agent 中即可。
其他接口细节无需关心。
"""
import asyncio
from impressmem import ImpressMemConfig, ImpressMemManager


async def main():
    # 初始化配置
    config = ImpressMemConfig(
        bot_name="Bot",
        redis_config={
            "host": "localhost",
            "port": 6379,
            "db": 1
        }
    )

    # 初始化 ImpressionManager
    manager = ImpressMemManager(config)

    try:
        # 构建记忆上下文 - 这是你需要使用的主要 API
        memory_context = await manager.build_memory_context()
        print("记忆上下文:")
        print("-" * 50)
        print(memory_context)
        print("-" * 50)

    finally:
        # 关闭连接
        await manager.close()


if __name__ == "__main__":
    asyncio.run(main())