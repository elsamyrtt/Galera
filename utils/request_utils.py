import logging
import random
import requests
from typing import Optional, Dict, Any

class RequestsManager:
    """
    Gestiona las solicitudes HTTP con soporte para user agents rotativos y proxies.
    """

    def __init__(
        self,
        use_proxies: bool = True,
        user_agent_rotation: bool = True,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 30,
        user_agents: Optional[list] = None
    ):
        """
        Inicializa el gestor de solicitudes.

        Args:
            use_proxies: Si se deben usar proxies
            user_agent_rotation: Si se deben rotar los user agents
            headers: Headers HTTP adicionales
            timeout: Tiempo de espera para solicitudes en segundos
            user_agents: Lista de user agents para rotar
        """
        self.logger = logging.getLogger("galera.RequestsManager")

        self.use_proxies = use_proxies
        self.user_agent_rotation = user_agent_rotation
        self.headers = headers or {}
        self.timeout = timeout
        self.user_agents = user_agents or [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.2 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 12_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.1 Mobile/15E148 Safari/605.1.15"
        ]

        self.current_user_agent = random.choice(self.user_agents)

    def get_headers(self) -> Dict[str, str]:
        """
        Obtiene los headers actuales para la solicitud.

        Returns:
            Diccionario con headers HTTP
        """
        headers = self.headers.copy()
        headers["User-Agent"] = self.current_user_agent
        return headers

    def rotate_user_agent(self) -> None:
        """
        Rota al siguiente user agent disponible.
        """
        self.current_user_agent = random.choice(self.user_agents)
        self.logger.info(f"User-Agent rotado a: {self.current_user_agent}")

    def get(self, url: str, **kwargs) -> requests.Response:
        """
        Realiza una solicitud GET con configuración personalizada.

        Args:
            url: URL objetivo
            kwargs: Argumentos adicionales para requests.get

        Returns:
            Respuesta HTTP
        """
        headers = self.get_headers()
        proxies = self._get_proxies() if self.use_proxies else None

        try:
            response = requests.get(
                url,
                headers=headers,
                proxies=proxies,
                timeout=self.timeout,
                **kwargs
            )
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            self.logger.error(f"Error en solicitud GET a {url}: {str(e)}")
            raise

    def post(self, url: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> requests.Response:
        """
        Realiza una solicitud POST con configuración personalizada.

        Args:
            url: URL objetivo
            data: Datos a enviar en el cuerpo de la solicitud
            kwargs: Argumentos adicionales para requests.post

        Returns:
            Respuesta HTTP
        """
        headers = self.get_headers()
        proxies = self._get_proxies() if self.use_proxies else None

        try:
            response = requests.post(
                url,
                headers=headers,
                proxies=proxies,
                data=data,
                timeout=self.timeout,
                **kwargs
            )
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            self.logger.error(f"Error en solicitud POST a {url}: {str(e)}")
            raise

    def _get_proxies(self) -> Optional[Dict[str, str]]:
        """
        Obtiene la configuración de proxies actual.

        Returns:
            Diccionario con configuración de proxies o None
        """
        # Aquí se podría integrar con ProxyManager para obtener un proxy actual
        # Por ahora, devolvemos un proxy ficticio
        return {
            "http": "http://127.0.0.1:8080",
            "https": "http://127.0.0.1:8080"
        }

    def get_timestamp(self) -> str:
        """
        Obtiene la marca de tiempo actual en formato ISO.

        Returns:
            Marca de tiempo en formato ISO
        """
        from datetime import datetime
        return datetime.now().isoformat()
