from openai import OpenAI
import pandas as pd
from dotenv import load_dotenv
import glob, os, sys
from datetime import datetime
import concurrent.futures

# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key from the environment variable
client = OpenAI(api_key=os.getenv("OPENAI_KEY"))

model = "gpt-4o"
max_tokens = 300

# Function to summarize an article using ChatGPT
def summarize_article(title, description, text):
    prompt = f"Title: {title}\nDescription: {description}\nText: {text}\n\nSummarize the above article."
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=max_tokens
    )
    return response.choices[0].message.content.strip()

# Function to score the summary
def score_summary(summary):
    scores = {}
    
    # Relevance to Current Trends
    trends_prompt = f"Analyze the summary for the mention of current tech trends such as AI, Machine Learning, or Blockchain. Rate the relevance on a scale from 1 to 5 based on trend alignment. Summary: {summary}"
    trends_response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant. For your responses, simply respond with a number."},
            {"role": "user", "content": trends_prompt}
        ],
        max_tokens=max_tokens
    )
    score = int(trends_response.choices[0].message.content.strip().replace('.', ''))
    scores['Relevance to Current Trends'] = score
    
    # Innovation Level
    innovation_prompt = f"Evaluate the novelty of the technology or development discussed in the summary. Rate the innovation level on a scale from 1 to 5, with 5 being highly novel or a breakthrough. Summary: {summary}"
    innovation_response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant. For your responses, simply respond with a number."},
            {"role": "user", "content": innovation_prompt}
        ],
        max_tokens=max_tokens
    )
    score = int(innovation_response.choices[0].message.content.strip().replace('.', ''))
    scores['Innovation Level'] = score
    
    # Practical Application
    application_prompt = f"Assess how the contents of the summary can be applied in real-world scenarios or projects. Rate the practical application on a scale from 1 to 5. Summary: {summary}"
    application_response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant. For your responses, simply respond with a number."},
            {"role": "user", "content": application_prompt}
        ],
        max_tokens=max_tokens
    )
    score = int(application_response.choices[0].message.content.strip().replace('.', ''))
    scores['Practical Application'] = score
    
    # Reader Engagement Indicators
    engagement_prompt = f"Review any available engagement data (comments, shares, likes) from social media or websites for the article summarized. Rate the engagement level on a scale from 1 to 5. Summary: {summary}"
    engagement_response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant. For your responses, simply respond with a number."},
            {"role": "user", "content": engagement_prompt}
        ],
        max_tokens=max_tokens
    )
    score = int(engagement_response.choices[0].message.content.strip().replace('.', ''))
    scores['Reader Engagement Indicators'] = score
    
    # Expert Opinions
    opinions_prompt = f"Check for and include any expert opinions or analyses related to the article. Rate the impact of these opinions on a scale from 1 to 5. Summary: {summary}"
    opinions_response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant. For your responses, simply respond with a number."},
            {"role": "user", "content": opinions_prompt}
        ],
        max_tokens=max_tokens
    )
    score = int(opinions_response.choices[0].message.content.strip().replace('.', ''))
    scores['Expert Opinions'] = score

    # Industry
    industry_prompt = f"Categorize the following summary as related to one of the 4 following industries: \n1. Tech News\n2. AI\n3. Web Development\n4. Big Data / DevOps\nThe response should only contain the name of the industry.\n\nSummary: {summary}"
    industry_response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": industry_prompt}
        ],
        max_tokens=max_tokens
    )
    industry = industry_response.choices[0].message.content.strip()
    
    # Aggregate the scores
    scores['Final Interesting-ness Score'] = sum(scores.values()) / len(scores)
    
    return scores, industry

# Function to process each article and collect summaries and scores
def process_article(row):
    try:
        text = row['Text'] if len(row['Text']) < 5000 else row['Text'][:4500]
        summary = summarize_article(row['Title'], row['Description'], text)
        scores, industry = score_summary(summary)
        return {
            'title': row['Title'],
            'summary': summary,
            'scores': scores,
            'final_scores': scores['Final Interesting-ness Score'],
            'industry': industry
        }
    except KeyboardInterrupt:
        sys.exit()
    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        return None

def summarize_and_score():
    # Load the DataFrame from the uploaded file
    texts = sorted(glob.glob('*_texts.csv'), key=os.path.getctime, reverse=True)
    df1 = pd.read_csv(texts[0])
    headlines = sorted(glob.glob('*_headlines.csv'), key=os.path.getctime, reverse=True)
    df2 = pd.read_csv(headlines[0])

    df = df1.merge(df2, left_on="URL", right_on="url", how="left")
    print(df.head())
    df = df.dropna()

    # Use threads to process articles in parallel
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_article, row) for index, row in df.iterrows()]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]

    # Filter out None results from any failed articles
    summaries_and_scores = [result for result in results if result]

    # Convert to DataFrame and save the results
    formatted_date = datetime.now().strftime('%y-%m-%d')
    results_df = pd.DataFrame(summaries_and_scores)
    results_df.to_csv(f'{formatted_date}_scores.csv', index=False)

if __name__ == "__main__":
    summarize_and_score()
