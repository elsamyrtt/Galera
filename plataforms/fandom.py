from galera.core.static_scrapper import StaticScraper
from bs4 import BeautifulSoup

class FandomScraper(StaticScraper):
    """
    Scraper especializado para Fandom.
    """

    def __init__(self, **kwargs):
        """
        Inicializa el scraper de Fandom con configuración base.
        """
        super().__init__(**kwargs)

    def scrape(self, url: str) -> dict:
        """
        Realiza scraping de una página de Fandom.

        Args:
            url: URL de la página de Fandom

        Returns:
            Diccionario con datos extraídos
        """
        self.logger.info(f"Iniciando scraping en Fandom: {url}")

        # Realizar scraping usando el método base
        data = super().scrape(url)

        # Extraer información específica de Fandom
        soup = BeautifulSoup(data['html'], 'html.parser')
        fandom_data = {
            "title": soup.find("h1", {"id": "WikiaArticleTitle"}).text if soup.find("h1", {"id": "WikiaArticleTitle"}) else "",
            "content": self._extract_content(soup)
        }

        # Combinar con datos base
        data.update(fandom_data)
        return data

    def _extract_content(self, soup: BeautifulSoup) -> str:
        """
        Extrae el contenido principal de una página de Fandom.

        Args:
            soup: Objeto BeautifulSoup con el contenido HTML

        Returns:
            Texto del contenido principal
        """
        content_div = soup.find("div", {"class": "mw-parser-output"})
        return content_div.text.strip() if content_div else ""
