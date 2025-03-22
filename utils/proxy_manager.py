import requests
import random
import time
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

class ProxyManager:
    """
    Administra una lista de proxies, con verificación y rotación automática.
    """
    
    def __init__(
        self,
        proxy_list: Optional[List[str]] = None,
        proxy_api_url: Optional[str] = None,
        proxy_api_key: Optional[str] = None,
        proxy_username: Optional[str] = None,
        proxy_password: Optional[str] = None,
        test_url: str = "https://httpbin.org/ip",
        max_failures: int = 3,
        verify_proxies: bool = True,
        refresh_interval: int = 3600,  # Segundos
        country_filter: Optional[List[str]] = None
    ):
        """
        Inicializa el administrador de proxies.
        
        Args:
            proxy_list: Lista de proxies en formato "ip:puerto"
            proxy_api_url: URL de API proveedora de proxies
            proxy_api_key: Clave API para servicio de proxies
            proxy_username: Usuario para proxies autenticados
            proxy_password: Contraseña para proxies autenticados
            test_url: URL para probar proxies
            max_failures: Máximo de fallos antes de descartar un proxy
            verify_proxies: Si se deben verificar los proxies
            refresh_interval: Intervalo para refrescar lista de proxies
            country_filter: Lista de códigos de país para filtrar proxies
        """
        self.logger = logging.getLogger("galera.ProxyManager")
        
        self.proxy_list = proxy_list or []
        self.proxy_api_url = proxy_api_url
        self.proxy_api_key = proxy_api_key
        self.proxy_username = proxy_username
        self.proxy_password = proxy_password
        self.test_url = test_url
        self.max_failures = max_failures
        self.verify_proxies = verify_proxies
        self.refresh_interval = refresh_interval
        self.country_filter = country_filter
        
        # Estado interno
        self.working_proxies = []
        self.failed_proxies = {}  # proxy -> contador de fallos
        self.current_proxy_index = 0
        self.last_refresh_time = None
        
        # Inicializar proxies
        if proxy_list or proxy_api_url:
            self.refresh_proxies()
    
    def refresh_proxies(self) -> None:
        """
        Actualiza la lista de proxies desde la fuente configurada.
        """
        self.logger.info("Actualizando lista de proxies")
        
        # Reiniciar estado interno
        self.working_proxies = []
        self.failed_proxies = {}
        self.current_proxy_index = 0
        
        # Obtener proxies desde API si está configurado
        if self.proxy_api_url:
            proxies = self._fetch_proxies_from_api()
            if proxies:
                self.proxy_list = proxies
        
        # Verificar y filtrar proxies
        if self.verify_proxies:
            self._verify_all_proxies()
        else:
            self.working_proxies = self.proxy_list.copy()
        
        self.last_refresh_time = datetime.now()
        
        self.logger.info(f"Lista de proxies actualizada: {len(self.working_proxies)} proxies disponibles")
    
    def _fetch_proxies_from_api(self) -> List[str]:
        """
        Obtiene proxies desde una API externa.
        
        Returns:
            Lista de proxies
        """
        try:
            params = {}
            if self.proxy_api_key:
                params['api_key'] = self.proxy_api_key
            if self.country_filter:
                params['country'] = ','.join(self.country_filter)
            
            response = requests.get(self.proxy_api_url, params=params, timeout=30)
            if response.status_code != 200:
                self.logger.error(f"Error al obtener proxies: {response.status_code}")
                return []
            
            # El formato de respuesta puede variar según el proveedor
            # Este es un ejemplo genérico
            data = response.json()
            if isinstance(data, dict) and 'proxies' in data:
                return [f"{p['ip']}:{p['port']}" for p in data['proxies']]
            elif isinstance(data, list):
                # Asumimos formato simple ["ip:port", ...]
                return data
            else:
                self.logger.error("Formato de respuesta de API de proxies no reconocido")
                return []
            
        except Exception as e:
            self.logger.error(f"Error al obtener proxies desde API: {str(e)}")
            return []
    
    def _verify_proxy(self, proxy: str) -> bool:
        """
        Verifica si un proxy funciona correctamente.
        
        Args:
            proxy: Proxy en formato "ip:puerto"
            
        Returns:
            True si el proxy funciona, False si no
        """
        proxies = {
            "http": f"http://{proxy}",
            "https": f"http://{proxy}"
        }
        
        # Añadir autenticación si está configurada
        if self.proxy_username and self.proxy_password:
            auth = f"{self.proxy_username}:{self.proxy_password}@"
            proxies = {
                "http": f"http://{auth}{proxy}",
                "https": f"http://{auth}{proxy}"
            }
        
        try:
            response = requests.get(
                self.test_url,
                proxies=proxies,
                timeout=10
            )
            return response.status_code == 200
        except Exception:
            return False
    
    def _verify_all_proxies(self) -> None:
        """
        Verifica todos los proxies disponibles y actualiza la lista de trabajando.
        """
        self.logger.info(f"Verificando {len(self.proxy_list)} proxies")
        
        working = []
        for proxy in self.proxy_list:
            if self._verify_proxy(proxy):
                working.append(proxy)
        
        self.working_proxies = working
        self.logger.info(f"{len(working)} proxies verificados y funcionando")
    
    def get_proxy(self) -> Optional[str]:
        """
        Obtiene el siguiente proxy disponible.
        
        Returns:
            Proxy en formato "ip:puerto" o None si no hay
        """
        # Verificar si es tiempo de refrescar los proxies
        if (self.last_refresh_time and 
            datetime.now() - self.last_refresh_time > timedelta(seconds=self.refresh_interval)):
            self.refresh_proxies()
        
        # Si no hay proxies disponibles
        if not self.working_proxies:
            return None
        
        # Seleccionar siguiente proxy
        if self.current_proxy_index >= len(self.working_proxies):
            self.current_proxy_index = 0
        
        proxy = self.working_proxies[self.current_proxy_index]
        self.current_proxy_index += 1
        
        # Formatear para autenticación si es necesario
        if self.proxy_username and self.proxy_password:
            return f"{self.proxy_username}:{self.proxy_password}@{proxy}"
        
        return proxy
    
    def rotate_proxy(self) -> Optional[str]:
        """
        Rota al siguiente proxy disponible.
        
        Returns:
            Nuevo proxy seleccionado
        """
        return self.get_proxy()
    
    def mark_proxy_failed(self, proxy: str) -> None:
        """
        Marca un proxy como fallido.
        
        Args:
            proxy: Proxy en formato "ip:puerto"
        """
        # Normalizar proxy (quitar autenticación si existe)
        if '@' in proxy:
            proxy = proxy.split('@')[1]
        
        # Incrementar contador de fallos
        self.failed_proxies[proxy] = self.failed_proxies.get(proxy, 0) + 1
        
        # Eliminar si supera el máximo de fallos
        if self.failed_proxies[proxy] >= self.max_failures:
            if proxy in self.working_proxies:
                self.working_proxies.remove(proxy)
                self.logger.info(f"Proxy {proxy} eliminado por fallos excesivos")
