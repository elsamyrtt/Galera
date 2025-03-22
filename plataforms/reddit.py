from ..core.dynamic_scrapper import DynamicScraper
from bs4 import BeautifulSoup

class RedditScraper(DynamicScraper):
    """
    Scraper especializado para Reddit.
    """

    def __init__(self, **kwargs):
        """
        Inicializa el scraper de Reddit con configuración base.
        """
        super().__init__(**kwargs)

    def scrape(self, url: str) -> dict:
        """
        Realiza scraping de una página de Reddit.

        Args:
            url: URL de la página de Reddit

        Returns:
            Diccionario con datos extraídos
        """
        self.logger.info(f"Iniciando scraping en Reddit: {url}")

        # Realizar scraping usando el método base
        data = super().scrape(url)

        # Extraer información específica de Reddit
        soup = BeautifulSoup(data['html'], 'html.parser')
        reddit_data = {
            "title": soup.find("h1").text if soup.find("h1") else "",
            "posts": self._extract_posts(soup)
        }

        # Combinar con datos base
        data.update(reddit_data)
        return data

    def _extract_posts(self, soup: BeautifulSoup) -> list:
        """
        Extrae las publicaciones de una página de Reddit.

        Args:
            soup: Objeto BeautifulSoup con el contenido HTML

        Returns:
            Lista de publicaciones
        """
        posts = []
        post_elements = soup.find_all("div", {"data-testid": "post-container"})
        for post in post_elements:
            post_data = {
                "title": post.find("h3").text if post.find("h3") else "",
                "author": post.find("a", {"data-testid": "post_author"}).text if post.find("a", {"data-testid": "post_author"}) else "",
                "content": post.find("div", {"data-testid": "post-content"}).text if post.find("div", {"data-testid": "post-content"}) else ""
            }
            posts.append(post_data)
        return posts
