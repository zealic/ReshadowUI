import cfscrape

scraper = cfscrape.create_scraper()

def get(url, allow_redirects = True):
    return scraper.get(url, allow_redirects=allow_redirects)

def get_content(url):
    return scraper.get(url).content
