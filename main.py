import time
from get_articles import get_articles
from get_texts import get_texts



def main():
    # this needs to work async
    get_articles()
    get_texts()
    # time.sleep(1)

   

if __name__ == "__main__":
    main()