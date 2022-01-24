from pynytimes import NYTAPI
from datetime import datetime, timedelta
nyt = NYTAPI('bKgOSmaa4IIJZdC0DE1G5ticaqGh6Qns', parse_dates=True)
from main import Stock
import requests

def search_nyt(my_query, begin, end, max_articles=5, delta=1):
    articles = nyt.article_search(
        query = my_query,
        results = max_articles,
        dates = {
            "begin": begin - timedelta(delta),
            "end": end + timedelta(delta)
        },
        options = {
            "sort": "relevance"
        }
    )[:max_articles]
    return articles

def filter(articles, relevant = ['abstract', 'pub_date', 'web_url']):
    new_articles = []
    for each in articles:
        new_articles.append([value for (key, value) in each.items() if key in relevant])
    return new_articles

def search_tickerTick(ticker, date, max_articles=5, delta=1):
    get_url = 'https://api.tickertick.com/feed'
    n = max_articles
    hours_ago = int((datetime.today() - date).total_seconds()/3600+24)
    q = "tt:{}".format(ticker)
    params = {'q': q, 'n': n, 'hours_ago': hours_ago}
    response = requests.get(get_url, params=params)
    return response

def extract_searchTick_response(response):
    stories = response.json()['stories']
    for story in stories:
        [story.pop(key) for key in ['id', 'favicon_url', 'tags']]
        story['time'] = datetime.fromtimestamp(story['time']/1000)
    return stories


def main():
    apple =  Stock("AAPL")
    gaussian_values = apple.get_gaussian_values(10)
    #apple.plot_min_max(gaussian_values)
    my_min, my_max = apple.get_min_max(gaussian_values)
    x = apple.df.index
    print(x[my_max])
    print(x[my_min])
    articles = search_tickerTick("Apple", x[my_min][0], x[my_min][0])