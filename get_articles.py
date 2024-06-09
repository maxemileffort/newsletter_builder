import requests
import pandas as pd
from datetime import datetime
import time
import os
from dotenv import load_dotenv

def newsapi_search_news(query, api_key):
    url = f'https://newsapi.org/v2/everything?q={query}&apiKey={api_key}&pageSize=10'
    response = requests.get(url)
    news_results = response.json()
    return news_results.get('articles', [])

def remove_duplicates_by_title(articles):
    unique_titles = set()
    unique_articles = []
    for article in articles:
        if article['title'] not in unique_titles:
            unique_titles.add(article['title'])
            unique_articles.append(article)
    return unique_articles

def get_articles():
    load_dotenv()

    api_key = os.getenv('NEWS_API_KEY')

    queries = ['latest AI advancements','AI technology news','AI releases past week',
               'AI industry impact','recent drone innovations','robotics advancements',
               'Boston Dynamics news','drone technology ','robotics industry updates',
               'NLP model updates','natural language processing news','latest NLP releases',
               'AI language models','tech companies NLP developments',
               'industrial robotics innovations','commercial robotics news','new robotic capabilities',
               'robotics applications industry','web development trends','latest web development tools',
               'web design advancements ','web functionality updates','React updates ',
               'Angular latest releases','Vue.js new features','web development frameworks news',
               'library enhancements web developers','big data technology news','latest big data tools',
               'big data applications finance healthcare retail','big data industry updates ',
               'latest DevOps innovations','DevOps trends ','new DevOps tools','deployment cycle improvements',
               'infrastructure management updates']

    all_articles = []

    for i, query in enumerate(queries):
        if i % 5 == 0:
            print(f'{round(i/len(queries)*100)}% done.')
        time.sleep(1)  # Pause for 1 second between queries
        articles = newsapi_search_news(query, api_key)
        for article in articles:
            article['query'] = query
        all_articles.extend(articles)

    unique_articles = remove_duplicates_by_title(all_articles)
    
    df = pd.DataFrame(unique_articles)
    formatted_date = datetime.now().strftime('%y-%m-%d')
    df.to_csv(f'{formatted_date}_headlines.csv', index=False)

    return df

if __name__ == "__main__":
    get_articles()
