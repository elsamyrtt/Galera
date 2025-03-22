import os
import multiprocessing
import asyncio
from typing import Dict, Any, List, Optional, Union, Callable
from concurrent.futures import ProcessPoolExecutor

from galera.core.base_scrapper import BaseScraper
from galera.core.static_scrapper import StaticScraper
from galera.core.dynamic_scrapper import DynamicScraper

class DistributedScraper:
    """
    Meta-scraper que coordina el scraping distribuido entre múltiples
    procesos y/o máquinas.
    """
    
    def __init__(
        self,
        scraper_type: str = "static",
        processes: int = None,
        chunk_size: int = 10,
        use_async: bool = True,
        max_concurrent_requests: int = 100,
        scraper_config: Optional[Dict[str, Any]] = None,
        custom_scraper: Optional[BaseScraper] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None,
        **kwargs
    ):
        """
        Inicializa el scraper distribuido.
        
        Args:
            scraper_type: Tipo de scraper a utilizar ("static", "dynamic")
            processes: Número de procesos a utilizar (por defecto: núcleos disponibles)
            chunk_size: Tamaño de los chunks para distribuir URLs
            use_async: Si se debe usar procesamiento asíncrono
            max_concurrent_requests: Máximo de solicitudes concurrentes
            scraper_config: Configuración personalizada para los scrapers
            custom_scraper: Instancia personalizada de scraper
            progress_callback: Función de callback para reportar progreso
        """
        self.scraper_type = scraper_type.lower()
        self.processes = processes if processes else multiprocessing.cpu_count()
        self.chunk_size = chunk_size
        self.use_async = use_async
        self.max_concurrent_requests = max_concurrent_requests
        self.scraper_config = scraper_config or {}
        self.custom_scraper = custom_scraper
        self.progress_callback = progress_callback
        
        # Combinar kwargs con scraper_config
        self.scraper_params = {**kwargs, **self.scraper_config}
        
        # Inicializar logger
        self.logger = self._setup_logger()
    
    def _setup_logger(self):
        """Configura y devuelve un logger para el scraper distribuido."""
        import logging
        
        logger = logging.getLogger("galera.DistributedScraper")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _create_scraper(self) -> BaseScraper:
        """
        Crea y devuelve una instancia del scraper configurado.
        
        Returns:
            Instancia de BaseScraper
        """
        if self.custom_scraper:
            return self.custom_scraper
        
        if self.scraper_type == "static":
            return StaticScraper(**self.scraper_params)
        elif self.scraper_type == "dynamic":
            return DynamicScraper(**self.scraper_params)
        else:
            raise ValueError(f"Tipo de scraper no válido: {self.scraper_type}")
    
    def _process_chunk(self, urls_chunk: List[str]) -> List[Dict[str, Any]]:
        """
        Procesa un chunk de URLs utilizando el scraper configurado.
        
        Args:
            urls_chunk: Lista de URLs para procesar
            
        Returns:
            Lista de resultados
        """
        scraper = self._create_scraper()
        
        if self.use_async and hasattr(scraper, 'scrape_multiple_async'):
            # Usar versión asíncrona si está disponible
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            results = loop.run_until_complete(scraper.scrape_multiple_async(urls_chunk))
            loop.close()
        else:
            # Usar versión sincrónica
            results = scraper.scrape_multiple(urls_chunk)
        
        return results
    
    def scrape(self, urls: List[str]) -> List[Dict[str, Any]]:
        """
        Realiza scraping distribuido de múltiples URLs.
        
        Args:
            urls: Lista de URLs para hacer scraping
            
        Returns:
            Lista de resultados
        """
        self.logger.info(f"Iniciando scraping distribuido de {len(urls)} URLs")
        
        # Calcular número de chunks
        total_chunks = (len(urls) + self.chunk_size - 1) // self.chunk_size
        
        # Dividir URLs en chunks
        url_chunks = [urls[i:i + self.chunk_size] for i in range(0, len(urls), self.chunk_size)]
        
        # Inicializar resultados
        all_results = []
        processed_chunks = 0
        
        # Procesar chunks en paralelo
        with ProcessPoolExecutor(max_workers=self.processes) as executor:
            # Mapear cada chunk a un proceso
            futures = [executor.submit(self._process_chunk, chunk) for chunk in url_chunks]
            
            # Recolectar resultados
            for future in futures:
                try:
                    chunk_results = future.result()
                    all_results.extend(chunk_results)
                    
                    # Actualizar progreso
                    processed_chunks += 1
                    if self.progress_callback:
                        self.progress_callback(processed_chunks, total_chunks)
                    
                    self.logger.info(f"Completado chunk {processed_chunks}/{total_chunks}")
                    
                except Exception as e:
                    self.logger.error(f"Error en chunk: {str(e)}")
        
        self.logger.info(f"Scraping distribuido completado. Procesados {len(all_results)} de {len(urls)} URLs")
        return all_results