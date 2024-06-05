
# News Scraper

This repository contains scripts for scraping news articles and their content, processing them, and saving the results into CSV files. The scripts utilize the NewsAPI to fetch headlines and a custom scraper to extract content from the article URLs. 

## Requirements

- Python 3.x
- Required Python packages: `requests`, `pandas`, `python-dotenv`, `concurrent.futures`
- NewsAPI key
- Custom scraper module (`scraper.py`)

## Setup

1. Clone the repository:

```sh
git clone https://github.com/yourusername/newsscraper.git
cd newsscraper
```

2. Install the required packages:

```sh
pip install requests pandas python-dotenv
```

3. Set up your environment variables:

Create a `.env` file in the root directory of the repository and add your API keys:

```env
NEWS_API_KEY=your_newsapi_key
OPENAI_KEY=your_openai_api_key
```

Get your News API key [here](https://newsapi.org/).
Get your OpenAI key [here](https://platform.openai.com/).

4. Ensure the `scraper.py` module is in the same directory as the other scripts. This module should contain the custom `Scraper` class used for extracting article content.

## Usage

### Get Articles

The `get_articles.py` script fetches news articles from the NewsAPI based on a set of predefined queries, removes duplicate articles by title, and saves the results to a CSV file.

#### Running the Script

```sh
python get_articles.py
```

This will generate a CSV file named `yy-mm-dd_headlines.csv` containing the fetched headlines.

### Get Texts

The `get_texts.py` script reads the latest headlines CSV file, processes each article URL using the custom scraper, and saves the extracted content to a new CSV file.

#### Running the Script

```sh
python get_texts.py
```

This will generate a CSV file named `yy-mm-dd_texts.csv` containing the extracted article contents.

### Main Script

The `main.py` script orchestrates the execution of both `get_articles.py` and `get_texts.py`.

#### Running the Script

```sh
python main.py
```

This script first runs the article fetching process, followed by the content extraction process, resulting in two CSV files: `yy-mm-dd_headlines.csv` and `yy-mm-dd_texts.csv`.

## Script Details

### get_articles.py

- Fetches news articles using the NewsAPI based on predefined queries.
- Removes duplicates by article title.
- Saves the results to `yy-mm-dd_headlines.csv`.

### get_texts.py

- Reads the latest headlines CSV file.
- Processes each article URL using the custom scraper.
- Saves the extracted content to `yy-mm-dd_texts.csv`.

### main.py

- Runs the `get_articles` and `get_texts` functions sequentially to generate the headlines and content CSV files.

## Example Queries

The `get_articles.py` script includes a list of example queries, such as:

- 'latest AI advancements'
- 'AI technology news'
- 'recent drone innovations'
- 'robotics advancements'
- 'web development trends'
- 'big data technology news'
- 'latest DevOps innovations'

You can modify these queries as needed to fetch articles on different topics.

## Contributing

Feel free to fork this repository and submit pull requests. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License.
