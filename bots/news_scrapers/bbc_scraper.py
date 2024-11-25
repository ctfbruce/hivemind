import feedparser
import requests
from bs4 import BeautifulSoup


rss_feed_urls = {
"us_and_canada" : "https://feeds.bbci.co.uk/news/world/us_and_canada/rss.xml",
"entertainment_and_arts" : "https://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml",
"top_stories" : "https://feeds.bbci.co.uk/news/rss.xml",
"science_and_environment" : "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml",
"politics":"https://feeds.bbci.co.uk/news/politics/rss.xml",
"education":"https://feeds.bbci.co.uk/news/education/rss.xml",
}

def scrape_rss_feed(feed_url = "http://feeds.bbci.co.uk/news/politics/rss.xml" ):
    feed = feedparser.parse(feed_url)
    
    return [{
        
        "title":entry["title"],
        "date":entry["published"],
        "summary":entry["summary"],
        "link":entry["link"]
        
    } for entry in feed["entries"]]
   

def scrape_page(url):
    # Fetch the HTML content
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch the page: {response.status_code}")
    
    # Parse the HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract <p> text inside each `data-component="text-block"` div
    text_blocks = []
    for text_block in soup.find_all("div", attrs={"data-component": "text-block"}):
        paragraphs = text_block.find_all("p")
        for p in paragraphs:
            text_blocks.append(p.get_text(strip=True))
    
    # Extract tags inside the <article> block
    article = soup.find("article")
    tags = []
    if article:
        tag_elements = article.find_all("div", attrs={"data-component": "tags"})
        for tag_element in tag_elements:
            tags.extend([tag.get_text(strip=True) for tag in tag_element.find_all("a")])
    
    return text_blocks, tags
    
def rss_scrape_to_prompt(feed_url):
    rss_dict = scrape_rss_feed(feed_url)
    
    return [f"{entry['title']}: {entry['summary']}" for entry in rss_dict]


def get_stories_from_topic(topic, number_of_headlines):
    if topic not in rss_feed_urls:
        raise KeyError(f"topic must be one of: {list(rss_feed_urls.keys())}")
    
    return(rss_scrape_to_prompt(rss_feed_urls[topic])[0:number_of_headlines])
    
    





