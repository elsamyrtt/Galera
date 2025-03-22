from bs4 import BeautifulSoup
from typing import List, Dict
from urllib.parse import urljoin

class ImageExtractor:
    """
    Extractor de imágenes de páginas web.
    """

    def extract(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """
        Extrae todas las imágenes de una página web.

        Args:
            soup: Objeto BeautifulSoup con el contenido HTML
            base_url: URL base para resolver rutas relativas

        Returns:
            Lista de diccionarios con detalles de las imágenes
        """
        images = []
        img_tags = soup.find_all('img')
        for img in img_tags:
            img_url = img.get('src')
            alt_text = img.get('alt', '')
            if img_url:
                img_url = urljoin(base_url, img_url)
                images.append({'src': img_url, 'alt': alt_text})
        return images
