from galera.core.dynamic_scrapper import DynamicScraper
from bs4 import BeautifulSoup

class TwitterScraper(DynamicScraper):
    """
    Scraper especializado para Twitter.
    """

    def __init__(self, **kwargs):
        """
        Inicializa el scraper de Twitter con configuración base.
        """
        super().__init__(**kwargs)

    def scrape(self, url: str) -> dict:
        """
        Realiza scraping de una página de Twitter.

        Args:
            url: URL de la página de Twitter

        Returns:
            Diccionario con datos extraídos
        """
        self.logger.info(f"Iniciando scraping en Twitter: {url}")

        # Realizar scraping usando el método base
        data = super().scrape(url)

        # Extraer información específica de Twitter
        soup = BeautifulSoup(data['html'], 'html.parser')
        twitter_data = {
            "tweets": self._extract_tweets(soup)
        }

        # Combinar con datos base
        data.update(twitter_data)
        return data

    def _extract_tweets(self, soup: BeautifulSoup) -> list:
        """
        Extrae los tweets de una página de Twitter.

        Args:
            soup: Objeto BeautifulSoup con el contenido HTML

        Returns:
            Lista de tweets
        """
        tweets = []
        tweet_elements = soup.find_all("article", {"data-testid": "tweet"})
        for tweet in tweet_elements:
            tweet_data = {
                "author": tweet.find("div", {"dir": "auto"}).text if tweet.find("div", {"dir": "auto"}) else "",
                "content": tweet.find("div", {"lang": "en"}).text if tweet.find("div", {"lang": "en"}) else ""
            }
            tweets.append(tweet_data)
        return tweets
