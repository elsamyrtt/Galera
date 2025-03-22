from bs4 import BeautifulSoup
from typing import List, Dict
from urllib.parse import urljoin

class LinkExtractor:
    """
    Extractor de enlaces de páginas web.
    """

    def extract(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """
        Extrae todos los enlaces de una página web.

        Args:
            soup: Objeto BeautifulSoup con el contenido HTML
            base_url: URL base para resolver rutas relativas

        Returns:
            Lista de diccionarios con detalles de los enlaces
        """
        links = []
        a_tags = soup.find_all('a', href=True)
        for a in a_tags:
            href = a.get('href')
            text = a.get_text(strip=True)
            if href:
                # Resolver rutas relativas
                full_url = urljoin(base_url, href)
                links.append({'href': full_url, 'text': text})
        return links
