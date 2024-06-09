import glob, os
import pandas as pd
from openai import OpenAI
import pandas as pd
from dotenv import load_dotenv
import glob, os, re, sys
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key from the environment variable
client = OpenAI(api_key=os.getenv("OPENAI_KEY"))

model = "gpt-4o"
max_tokens = 1500

def rank_and_sort():
    scores = sorted(glob.glob('*_scores.csv'), key=os.path.getctime, reverse=True)
    df1 = pd.read_csv(scores[0], sep="|")
    df1 = df1[df1['final_scores']>3.5]
    df1 = df1.sort_values(['industry', 'final_scores'], ascending=[True, False])
    df1 = df1.reset_index(drop=True)
    return df1

def generate_tutorial_ideas(title, summary, industry):
    prompt = f"""
    Based on the following article:
    Title: {title}
    Summary: {summary}
    Industry: {industry}
    
    Generate 5-10 tutorial ideas that relate directly to the technologies or innovations discussed. Each tutorial idea should include a brief outline of the objectives, the programming language used, the key skills or technologies to be covered, and how the tutorial aligns with current industry needs or practices.
    """
    
    response = client.chat.completions.create(
        model=model, 
        messages=[
            {"role": "system", "content": "You are a helpful assistant. You are direct in your responses, with little fluff or explanation, unless asked for."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=max_tokens
    )
    
    return response.choices[0].message.content.strip()

def process_article(row):
    title = row['title']
    summary = row['summary']
    industry = row['industry']
    ideas = generate_tutorial_ideas(title, summary, industry)
    return {
        'title': title,
        'summary': summary,
        'industry': industry,
        'tutorial_ideas': ideas
    }

def process_articles_concurrently(df):
    tutorial_ideas = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(process_article, row): index for index, row in df.iterrows()}
        for future in as_completed(futures):
            index = futures[future]
            try:
                result = future.result()
                tutorial_ideas.append(result)
                print(f"Completed processing article {index+1}/{len(df)}")
            except Exception as e:
                print(f"Error processing article {index+1}: {e}")

    return pd.DataFrame(tutorial_ideas)

def brainstorm_ideas():
    df = rank_and_sort()

    tut_df = process_articles_concurrently(df)
    print(tut_df)
    # Save the results to a CSV file if needed
    formatted_date = datetime.now().strftime('%y-%m-%d')
    tut_df.to_csv(f'{formatted_date}_tutorial_ideas.csv', index=False, sep="|")
         
    return

if __name__ == "__main__":
    brainstorm_ideas()