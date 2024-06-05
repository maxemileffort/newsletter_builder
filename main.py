from get_articles import get_articles
from get_texts import get_texts
import asyncio

async def main():
    # this needs to work async
    await get_articles()
    await get_texts()

if __name__ == "__main__":
    asyncio.run(main())
