import pandas as pd
from datetime import datetime
import glob, os
from scraper import Scraper
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio

def scrape_url(url):
    try:
        base_scrape = Scraper.transform_url(url)
        if isinstance(base_scrape, list):
            print(url)
            return None

        if base_scrape.check_if_pdf():
            print(url)
            return None

        base_scrape.useragent_generator()
        base_scrape.build_headers()
        base_scrape.get_domain()
        base_scrape.get_reading_data()
        base_scrape.get_title()
        base_scrape.get_word_count()
        
        if not isinstance(base_scrape.reading, str):
            text = base_scrape.reading.cleaned_text
        else:
            text = base_scrape.reading

        values = [base_scrape.title, base_scrape.domain, base_scrape.description, text,
                  base_scrape.image, base_scrape.word_count, url.strip()]
        return values
    except Exception as e:
        print(f"Error processing {url}: {e}")
        return None

async def get_texts():
    csvs = sorted(glob.glob('*_headlines.csv'), key=os.path.getctime, reverse=True)
    df = pd.read_csv(csvs[0])

    all_values = []
    num_threads = 10

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        loop = asyncio.get_event_loop()
        futures = [loop.run_in_executor(executor, scrape_url, url) for url in df['url']]
        for i, future in enumerate(await asyncio.gather(*futures)):
            if i % 10 == 0:
                print(f'{round(i/len(df)*100)}% done.')
            if future:
                all_values.append(future)

    # Create a DataFrame and save it to a CSV
    columns = ['Title', 'Domain', 'Description', 'Text', 'Image', 'WordCount', 'URL']
    result_df = pd.DataFrame(all_values, columns=columns)
    formatted_date = datetime.now().strftime('%y-%m-%d')
    result_df.to_csv(f'{formatted_date}_texts.csv', index=False)

if __name__ == "__main__":
    asyncio.run(get_texts())
