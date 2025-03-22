import aiohttp,asyncio,random,requests
from typing import Dict, Any, Optional, List
from bs4 import BeautifulSoup

from galera.core.base_scrapper import BaseScraper
from galera.extractor.text_extractor import TextExtractor
from galera.extractor.image_extractor import ImageExtractor
from galera.extractor.link_extractor import LinkExtractor
from galera.extractor.video_extractor import VideoExtractor

class StaticScraper(BaseScraper):
    """
    Scraper para páginas HTML estáticas utilizando BeautifulSoup.
    """
    
    def __init__(self, **kwargs):
        """
        Inicializa el scraper estático con la configuración base y extractores.
        """
        super().__init__(**kwargs)
        
        # Inicializar extractores
        self.text_extractor = TextExtractor()
        self.image_extractor = ImageExtractor()
        self.link_extractor = LinkExtractor()
        self.video_extractor = VideoExtractor()
    
    def scrape(self, url: str) -> Dict[str, Any]:
        """
        Realiza scraping de una URL estática usando BeautifulSoup.
        
        Args:
            url: URL objetivo
            
        Returns:
            Diccionario con datos extraídos
        """
        self.logger.info(f"Iniciando scraping estático en {url}")
        
        for attempt in range(self.retry_attempts):
            try:
                # Obtener contenido
                response = self.request_manager.get(url)
                
                # Verificar bloqueo
                if self.check_for_blocking(response):
                    self.handle_blocking(url, response)
                    continue
                
                # Verificar captcha
                captcha_solution = self.handle_captcha(response.text)
                if captcha_solution:
                    # Reenviar solicitud con solución de captcha
                    response = self.request_manager.get(
                        url, 
                        params={"captcha_solution": captcha_solution}
                    )
                
                # Parsear HTML
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extraer datos
                result = {
                    "url": url,
                    "title": soup.title.text if soup.title else "",
                    "text": self.text_extractor.extract(soup),
                    "images": self.image_extractor.extract(soup, base_url=url),
                    "links": self.link_extractor.extract(soup, base_url=url),
                    "videos": self.video_extractor.extract(soup, base_url=url),
                    "html": response.text,
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "timestamp": self.request_manager.get_timestamp()
                }
                
                self._random_delay()
                return result
                
            except Exception as e:
                self.logger.error(f"Error en intento {attempt+1}/{self.retry_attempts} para {url}: {str(e)}")
                if attempt < self.retry_attempts - 1:
                    self._random_delay()
                    # Rotar proxy y user agent para el siguiente intento
                    if self.use_proxies:
                        self.proxy_manager.rotate_proxy()
                    if self.user_agent_rotation:
                        self.request_manager.rotate_user_agent()
                else:
                    # Último intento fallido
                    return {
                        "url": url,
                        "error": str(e),
                        "status": "failed",
                        "timestamp": self.request_manager.get_timestamp()
                    }

    async def scrape_async(self, url: str) -> Dict[str, Any]:
        """
        Versión asíncrona del scraper estático.
        
        Args:
            url: URL objetivo
            
        Returns:
            Diccionario con datos extraídos
        """
        self.logger.info(f"Iniciando scraping estático asíncrono en {url}")
        
        for attempt in range(self.retry_attempts):
            try:
                # Obtener contenido
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        url,
                        headers=self.request_manager.get_headers(),
                        proxy=self.proxy_manager.get_proxy() if self.use_proxies else None,
                        timeout=self.timeout
                    ) as response:
                        html = await response.text()
                        status = response.status
                        headers = dict(response.headers)
                
                # Verificar captcha
                captcha_solution = self.handle_captcha(html)
                if captcha_solution:
                    # Reenviar solicitud con solución de captcha (simplificado)
                    async with aiohttp.ClientSession() as session:
                        async with session.get(
                            url,
                            params={"captcha_solution": captcha_solution},
                            headers=self.request_manager.get_headers(),
                            proxy=self.proxy_manager.get_proxy() if self.use_proxies else None,
                            timeout=self.timeout
                        ) as response:
                            html = await response.text()
                            status = response.status
                            headers = dict(response.headers)
                
                # Parsear HTML
                soup = BeautifulSoup(html, 'html.parser')
                
                # Extraer datos
                result = {
                    "url": url,
                    "title": soup.title.text if soup.title else "",
                    "text": self.text_extractor.extract(soup),
                    "images": self.image_extractor.extract(soup, base_url=url),
                    "links": self.link_extractor.extract(soup, base_url=url),
                    "videos": self.video_extractor.extract(soup, base_url=url),
                    "html": html,
                    "status_code": status,
                    "headers": headers,
                    "timestamp": self.request_manager.get_timestamp()
                }
                
                # Simular delay (para versión async usar asyncio.sleep)
                await asyncio.sleep(random.uniform(self.request_delay[0], self.request_delay[1]))
                return result
                
            except Exception as e:
                self.logger.error(f"Error en intento asíncrono {attempt+1}/{self.retry_attempts} para {url}: {str(e)}")
                if attempt < self.retry_attempts - 1:
                    await asyncio.sleep(random.uniform(1, 3))
                    # Rotar proxy y user agent para el siguiente intento
                    if self.use_proxies:
                        self.proxy_manager.rotate_proxy()
                    if self.user_agent_rotation:
                        self.request_manager.rotate_user_agent()
                else:
                    # Último intento fallido
                    return {
                        "url": url,
                        "error": str(e),
                        "status": "failed",
                        "timestamp": self.request_manager.get_timestamp()
                    }