from galera.core.dynamic_scrapper import DynamicScraper
from bs4 import BeautifulSoup

class LinkedInScraper(DynamicScraper):
    """
    Scraper especializado para LinkedIn.
    """

    def __init__(self, **kwargs):
        """
        Inicializa el scraper de LinkedIn con configuración base.
        """
        super().__init__(**kwargs)

    def scrape(self, url: str) -> dict:
        """
        Realiza scraping de una página de LinkedIn.

        Args:
            url: URL de la página de LinkedIn

        Returns:
            Diccionario con datos extraídos
        """
        self.logger.info(f"Iniciando scraping en LinkedIn: {url}")

        # Realizar scraping usando el método base
        data = super().scrape(url)

        # Extraer información específica de LinkedIn
        soup = BeautifulSoup(data['html'], 'html.parser')
        linkedin_data = {
            "profile": self._extract_profile(soup)
        }

        # Combinar con datos base
        data.update(linkedin_data)
        return data

    def _extract_profile(self, soup: BeautifulSoup) -> dict:
        """
        Extrae el perfil de una página de LinkedIn.

        Args:
            soup: Objeto BeautifulSoup con el contenido HTML

        Returns:
            Diccionario con datos del perfil
        """
        profile_data = {
            "name": soup.find("h1").text if soup.find("h1") else "",
            "headline": soup.find("h2").text if soup.find("h2") else "",
            "summary": soup.find("p", {"class": "pv-about__summary-text"}).text if soup.find("p", {"class": "pv-about__summary-text"}) else ""
        }
        return profile_data
