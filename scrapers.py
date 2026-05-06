import requests
from bs4 import BeautifulSoup

# ---- ITALIEN : La Stampa ----
def fetch_article_italian():
    url = "https://www.lastampa.it/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    links = [a['href'] for a in soup.find_all('a', href=True) if '/cronaca/' in a['href']]

    for link in links:
        article_url = link if link.startswith("http") else f"https://www.lastampa.it{link}"
        article_resp = requests.get(article_url)
        article_soup = BeautifulSoup(article_resp.content, "html.parser")

        title = article_soup.find('h1').get_text(strip=True) if article_soup.find('h1') else None

        story_div = article_soup.find('div', class_='story__text')
        if story_div:
            paragraphs = story_div.find_all('p')
            content = " ".join(p.get_text() for p in paragraphs)

            if content and len(content) > 500:
                return title, article_url, content

    return None, None, None


# ---- ALLEMAND : Tagesschau ----
def fetch_article_german():
    url = "https://www.tagesschau.de"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    links = [
        a['href'] for a in soup.find_all('a', href=True)
        if a['href'].startswith("/")
        and a['href'].endswith(".html")
        and "multimedia" not in a['href']
    ]

    for link in links:
        try:
            article_url = f"https://www.tagesschau.de{link}"
            article_resp = requests.get(article_url)
            article_soup = BeautifulSoup(article_resp.content, "html.parser")

            title_el = article_soup.find("h1")
            if not title_el:
                continue

            title = title_el.get_text(strip=True)

            paragraphs = [
                p.get_text(strip=True)
                for p in article_soup.find_all("p")
                if len(p.get_text(strip=True)) > 50
            ]

            content = " ".join(paragraphs)

            if len(content) > 300:
                return title, article_url, content

        except Exception:
            pass

    return None, None, None
