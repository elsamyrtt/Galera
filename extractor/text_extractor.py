from bs4 import BeautifulSoup
from typing import List

class TextExtractor:
    """
    Extractor de texto de páginas web.
    """

    def extract(self, soup: BeautifulSoup) -> str:
        """
        Extrae todo el texto de una página web.

        Args:
            soup: Objeto BeautifulSoup con el contenido HTML

        Returns:
            Texto extraído
        """
        # Extraer texto de todos los elementos de párrafo y encabezados
        paragraphs = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        text = ' '.join([para.get_text(strip=True) for para in paragraphs])
        return text
