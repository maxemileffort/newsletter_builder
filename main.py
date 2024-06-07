from get_articles import get_articles
from get_texts import get_texts
from summarize_and_score import summarize_and_score
import asyncio

async def main():
    # this needs to work async
    await get_articles()
    await get_texts()
    # summarize and score articles based on area
    await summarize_and_score()
    # take top 5 articles by score and brainstorm project ideas

    # create project file structure

    # outlime each key file in pseudocode

if __name__ == "__main__":
    asyncio.run(main())
