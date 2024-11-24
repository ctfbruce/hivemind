from active import political_tweet_generator
from news_scrapers import bbc_scraper



for prompt in bbc_scraper.main():
    political_tweet_generator.main(prompt)