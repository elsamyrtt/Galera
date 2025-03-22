from galera.core.static_scrapper import StaticScraper
from bs4 import BeautifulSoup

class WikipediaScraper(StaticScraper):
    """
    Scraper especializado para Wikipedia.
    """

    def __init__(self, **kwargs):
        """
        Inicializa el scraper de Wikipedia con configuración base.
        """
        super().__init__(**kwargs)

    def scrape(self, url: str) -> dict:
        """
        Realiza scraping de una página de Wikipedia.

        Args:
            url: URL de la página de Wikipedia

        Returns:
            Diccionario con datos extraídos
        """
        self.logger.info(f"Iniciando scraping en Wikipedia: {url}")

        # Realizar scraping usando el método base
        data = super().scrape(url)

        # Extraer información específica de Wikipedia
        soup = BeautifulSoup(data['html'], 'html.parser')
        wiki_data = {
            "title": soup.find("h1", {"id": "firstHeading"}).text if soup.find("h1", {"id": "firstHeading"}) else "",
            "intro": self._extract_intro(soup),
            "content": self._extract_content(soup),
            "references": self._extract_references(soup)
        }

        # Combinar con datos base
        data.update(wiki_data)
        return data

    def _extract_intro(self, soup: BeautifulSoup) -> str:
        """
        Extrae el párrafo de introducción de una página de Wikipedia.

        Args:
            soup: Objeto BeautifulSoup con el contenido HTML

        Returns:
            Texto de la introducción
        """
        intro_paragraph = soup.find("p", recursive=False)
        return intro_paragraph.text.strip() if intro_paragraph else ""

    def _extract_content(self, soup: BeautifulSoup) -> str:
        """
        Extrae el contenido principal de una página de Wikipedia.

        Args:
            soup: Objeto BeautifulSoup con el contenido HTML

        Returns:
            Texto del contenido principal
        """
        content_div = soup.find("div", {"class": "mw-parser-output"})
        return content_div.text.strip() if content_div else ""

    def _extract_references(self, soup: BeautifulSoup) -> list:
        """
        Extrae las referencias de una página de Wikipedia.

        Args:
            soup: Objeto BeautifulSoup con el contenido HTML

        Returns:
            Lista de referencias
        """
        references = []
        ref_section = soup.find("ol", {"class": "references"})
        if ref_section:
            for li in ref_section.find_all("li"):
                ref_text = li.text.strip()
                references.append(ref_text)
        return references
