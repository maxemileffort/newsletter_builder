from get_articles import get_articles
from get_texts import get_texts
from summarize_and_score import summarize_and_score
from brainstorm_ideas import rank_and_sort, brainstorm_ideas
import asyncio

async def main():
    # get articles and their content
    get_articles()
    get_texts()
    # summarize and score articles based on area
    summarize_and_score()
    # take top 5 articles by score and brainstorm project ideas
    brainstorm_ideas()
    # create project file structure

    # outlime each key file in pseudocode

if __name__ == "__main__":
    asyncio.run(main())
