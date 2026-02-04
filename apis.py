import feedparser

def news():
    url = "https://news.google.com/rss?hl=fi&gl=FI&ceid=FI:fi"
    feed = feedparser.parse(url)
    spaces = ""
    spaces = " " * 14 + spaces + "" * 14
    headline = [entry.title for entry in feed.entries[:5]]
    return spaces.join(headline)
    for headline in headlines:
        return headline
if __name__ == "__main__":
    print(news())