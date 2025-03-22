import logging
import time
import random
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
from concurrent.futures import ThreadPoolExecutor
import multiprocessing
import asyncio
import aiohttp

from ..utils.proxy_manager import ProxyManager
from ..utils.human_behavior import HumanBehaviorSimulator
from ..utils.captcha_solver import CaptchaSolver
from ..utils.request_utils import RequestsManager

class BaseScraper(ABC):
    """
    Clase base para todos los scrapers de Galera.
    Define la interfaz común y funcionalidades básicas.
    """
    
    def __init__(
        self,
        use_proxies: bool = True,
        simulate_human: bool = True,
        solve_captchas: bool = True,
        concurrency: int = 10,
        retry_attempts: int = 3,
        request_delay: tuple = (1, 5),
        user_agent_rotation: bool = True,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 30,
        logger: Optional[logging.Logger] = None,
    ):
        """
        Inicializa el scraper base con configuraciones comunes.
        
        Args:
            use_proxies: Si se deben usar proxies para las solicitudes
            simulate_human: Si se debe simular comportamiento humano
            solve_captchas: Si se deben resolver captchas automáticamente
            concurrency: Número máximo de solicitudes concurrentes
            retry_attempts: Número de intentos antes de fallar
            request_delay: Tupla (min, max) para pausas entre solicitudes
            user_agent_rotation: Si se deben rotar los user agents
            headers: Headers HTTP adicionales
            timeout: Tiempo de espera para solicitudes en segundos
            logger: Logger personalizado
        """
        self.use_proxies = use_proxies
        self.simulate_human = simulate_human
        self.solve_captchas = solve_captchas
        self.concurrency = concurrency
        self.retry_attempts = retry_attempts
        self.request_delay = request_delay
        self.user_agent_rotation = user_agent_rotation
        self.headers = headers or {}
        self.timeout = timeout
        
        # Configurar logger
        self.logger = logger or self._setup_logger()
        
        # Inicializar componentes utilitarios
        if use_proxies:
            self.proxy_manager = ProxyManager()
        
        if simulate_human:
            self.human_simulator = HumanBehaviorSimulator()
        
        if solve_captchas:
            self.captcha_solver = CaptchaSolver()
        
        self.request_manager = RequestsManager(
            use_proxies=use_proxies,
            user_agent_rotation=user_agent_rotation,
            headers=headers,
            timeout=timeout
        )
    
    def _setup_logger(self) -> logging.Logger:
        """Configura y devuelve un logger para el scraper."""
        logger = logging.getLogger(f"galera.{self.__class__.__name__}")
        logger.setLevel(logging.INFO)
        
        # Evitar duplicación de handlers
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _random_delay(self) -> None:
        """Introduce una pausa aleatoria para simular comportamiento humano."""
        if self.simulate_human:
            delay = random.uniform(self.request_delay[0], self.request_delay[1])
            time.sleep(delay)
    
    @abstractmethod
    def scrape(self, url: str) -> Dict[str, Any]:
        """
        Método principal para realizar scraping de una URL.
        Debe ser implementado por las subclases.
        
        Args:
            url: URL objetivo para hacer scraping
            
        Returns:
            Diccionario con datos extraídos
        """
        pass
    
    def scrape_multiple(self, urls: List[str], parallel: bool = True) -> List[Dict[str, Any]]:
        """
        Realiza scraping de múltiples URLs en paralelo o secuencialmente.
        
        Args:
            urls: Lista de URLs para hacer scraping
            parallel: Si se debe usar procesamiento paralelo
            
        Returns:
            Lista de diccionarios con datos extraídos
        """
        self.logger.info(f"Iniciando scraping de {len(urls)} URLs")
        
        if not parallel:
            return [self.scrape(url) for url in urls]
        
        # Usar ThreadPoolExecutor para paralelismo
        results = []
        with ThreadPoolExecutor(max_workers=self.concurrency) as executor:
            future_to_url = {executor.submit(self.scrape, url): url for url in urls}
            for future in future_to_url:
                try:
                    data = future.result()
                    results.append(data)
                except Exception as exc:
                    self.logger.error(f"Error al hacer scraping de {future_to_url[future]}: {exc}")
        
        return results
    
    async def scrape_async(self, url: str) -> Dict[str, Any]:
        """
        Versión asíncrona del método scrape.
        Debe ser implementado por las subclases que soporten asyncio.
        
        Args:
            url: URL objetivo para hacer scraping
            
        Returns:
            Diccionario con datos extraídos
        """
        raise NotImplementedError("La implementación asíncrona debe ser proporcionada por las subclases")
    
    async def scrape_multiple_async(self, urls: List[str]) -> List[Dict[str, Any]]:
        """
        Realiza scraping asíncrono de múltiples URLs.
        
        Args:
            urls: Lista de URLs para hacer scraping
            
        Returns:
            Lista de diccionarios con datos extraídos
        """
        self.logger.info(f"Iniciando scraping asíncrono de {len(urls)} URLs")
        
        tasks = [self.scrape_async(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filtrar errores
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(f"Error al hacer scraping asíncrono de {urls[i]}: {result}")
            else:
                processed_results.append(result)
        
        return processed_results
    
    def scrape_distributed(self, urls: List[str], processes: int = None) -> List[Dict[str, Any]]:
        """
        Realiza scraping distribuido usando multiprocessing.
        
        Args:
            urls: Lista de URLs para hacer scraping
            processes: Número de procesos a utilizar (por defecto: núcleos disponibles)
            
        Returns:
            Lista de diccionarios con datos extraídos
        """
        self.logger.info(f"Iniciando scraping distribuido de {len(urls)} URLs")
        
        if processes is None:
            processes = multiprocessing.cpu_count()
        
        # Dividir URLs en chunks para cada proceso
        chunk_size = max(1, len(urls) // processes)
        url_chunks = [urls[i:i + chunk_size] for i in range(0, len(urls), chunk_size)]
        
        # Crear pool de procesos
        with multiprocessing.Pool(processes=processes) as pool:
            # Map scrape_multiple a cada chunk
            chunk_results = pool.map(self.scrape_multiple, url_chunks)
        
        # Aplanar resultados
        results = [item for sublist in chunk_results for item in sublist]
        return results
        
    def handle_captcha(self, html_content: str) -> Optional[str]:
        """
        Detecta y resuelve captchas si están presentes.
        
        Args:
            html_content: Contenido HTML que puede contener captcha
            
        Returns:
            Solución al captcha o None si no hay captcha
        """
        if not self.solve_captchas:
            return None
        
        return self.captcha_solver.solve(html_content)
    
    def check_for_blocking(self, response) -> bool:
        """
        Verifica si la respuesta indica bloqueo o limitación de acceso.
        
        Args:
            response: Objeto de respuesta HTTP
            
        Returns:
            True si se detecta bloqueo, False en caso contrario
        """
        # Códigos comunes de bloqueo
        if response.status_code in (403, 429, 503):
            self.logger.warning(f"Posible bloqueo detectado (código {response.status_code})")
            return True
        
        # Buscar indicadores comunes de bloqueo en el contenido
        block_indicators = [
            "captcha", "blocked", "rate limit", "too many requests",
            "access denied", "forbidden", "ip has been blocked"
        ]
        
        content_lower = response.text.lower()
        for indicator in block_indicators:
            if indicator in content_lower:
                self.logger.warning(f"Posible bloqueo detectado (indicador: {indicator})")
                return True
        
        return False
    
    def handle_blocking(self, url: str, response) -> None:
        """
        Maneja situaciones de bloqueo activando medidas de evasión.
        
        Args:
            url: URL donde se detectó bloqueo
            response: Objeto de respuesta HTTP
        """
        self.logger.info(f"Activando medidas anti-bloqueo para {url}")
        
        # Cambiar proxy si está habilitado
        if self.use_proxies:
            self.proxy_manager.rotate_proxy()
        
        # Rotar user agent
        if self.user_agent_rotation:
            self.request_manager.rotate_user_agent()
        
        # Aumentar delay
        self._random_delay()
        self._random_delay()  # Doble delay para mayor seguridad