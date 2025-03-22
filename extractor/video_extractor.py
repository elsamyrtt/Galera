from bs4 import BeautifulSoup
from typing import List, Dict
from urllib.parse import urljoin

class VideoExtractor:
    """
    Extractor de videos de páginas web.
    """

    def extract(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """
        Extrae todos los videos de una página web.

        Args:
            soup: Objeto BeautifulSoup con el contenido HTML
            base_url: URL base para resolver rutas relativas

        Returns:
            Lista de diccionarios con detalles de los videos
        """
        videos = []
        video_tags = soup.find_all('video')
        for video in video_tags:
            src = video.get('src')
            poster = video.get('poster', '')
            if src:
                src = urljoin(base_url, src)
                videos.append({'src': src, 'poster': poster})
        return videos
