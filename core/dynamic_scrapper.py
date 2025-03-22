from typing import Dict, Any, Optional, List, Union
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from bs4 import BeautifulSoup

from .base_scraper import BaseScraper
from ..extractors.text_extractor import TextExtractor
from ..extractors.image_extractor import ImageExtractor
from ..extractors.link_extractor import LinkExtractor
from ..extractors.video_extractor import VideoExtractor
from ..extractors.api_extractor import ApiExtractor

class DynamicScraper(BaseScraper):
    """
    Scraper para páginas con contenido dinámico generado por JavaScript
    utilizando Selenium.
    """
    
    def __init__(
        self,
        browser_type: str = "chrome",
        headless: bool = True,
        window_size: tuple = (1920, 1080),
        load_timeout: int = 30,
        scroll_timeout: int = 5,
        scroll_pause: float = 1.0,
        max_scroll_attempts: int = 10,
        wait_for_network_idle: bool = True,
        chrome_options: Optional[Options] = None,
        browser_executable_path: Optional[str] = None,
        handle_shadow_dom: bool = True,
        handle_iframes: bool = True,
        extract_xhr: bool = True,
        **kwargs
    ):
        """
        Inicializa el scraper dinámico con Selenium.
        
        Args:
            browser_type: Tipo de navegador a utilizar ('chrome', 'firefox')
            headless: Si se debe ejecutar en modo headless
            window_size: Tamaño de la ventana (ancho, alto)
            load_timeout: Tiempo de espera para carga de página
            scroll_timeout: Tiempo de espera entre scrolls
            scroll_pause: Pausa entre scrolls para cargar contenido
            max_scroll_attempts: Máximo número de intentos de scroll
            wait_for_network_idle: Esperar a que la red esté inactiva
            chrome_options: Opciones personalizadas para Chrome
            browser_executable_path: Ruta al ejecutable del navegador
            handle_shadow_dom: Si se debe manejar Shadow DOM
            handle_iframes: Si se deben manejar iframes
            extract_xhr: Si se deben extraer solicitudes XHR
        """
        super().__init__(**kwargs)
        
        self.browser_type = browser_type
        self.headless = headless
        self.window_size = window_size
        self.load_timeout = load_timeout
        self.scroll_timeout = scroll_timeout
        self.scroll_pause = scroll_pause
        self.max_scroll_attempts = max_scroll_attempts
        self.wait_for_network_idle = wait_for_network_idle
        self.chrome_options = chrome_options
        self.browser_executable_path = browser_executable_path
        self.handle_shadow_dom = handle_shadow_dom
        self.handle_iframes = handle_iframes
        self.extract_xhr = extract_xhr
        
        # Inicializar extractores
        self.text_extractor = TextExtractor()
        self.image_extractor = ImageExtractor()
        self.link_extractor = LinkExtractor()
        self.video_extractor = VideoExtractor()
        self.api_extractor = ApiExtractor()
        
        # WebDriver inicialmente None, se inicializa en _setup_browser
        self.driver = None
    
    def _setup_browser(self) -> webdriver.Chrome:
        """
        Configura y devuelve una instancia del navegador.
        
        Returns:
            Instancia del WebDriver
        """
        # Configurar opciones para Chrome (por defecto)
        if self.browser_type.lower() == "chrome":
            options = self.chrome_options if self.chrome_options else Options()
            
            if self.headless:
                options.add_argument("--headless")
            
            options.add_argument(f"--window-size={self.window_size[0]},{self.window_size[1]}")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--no-sandbox")
            
            # Configurar user agent
            if self.user_agent_rotation:
                options.add_argument(f"user-agent={self.request_manager.get_user_agent()}")
            
            # Configurar proxy si está habilitado
            if self.use_proxies:
                proxy = self.proxy_manager.get_proxy()
                if proxy:
                    options.add_argument(f'--proxy-server={proxy}')
            
            # Inicializar driver
            if self.browser_executable_path:
                return webdriver.Chrome(executable_path=self.browser_executable_path, options=options)
            else:
                return webdriver.Chrome(options=options)
        
        elif self.browser_type.lower() == "firefox":
            # Similar configuración para Firefox
            options = webdriver.FirefoxOptions()
            if self.headless:
                options.add_argument("--headless")
            
            # Resto de configuración similar a Chrome...
            
            if self.browser_executable_path:
                return webdriver.Firefox(executable_path=self.browser_executable_path, options=options)
            else:
                return webdriver.Firefox(options=options)
        
        else:
            raise ValueError(f"Tipo de navegador no soportado: {self.browser_type}")
    
    def _scroll_to_bottom(self, driver: webdriver.Chrome) -> bool:
        """
        Desplaza la página hasta el final para cargar contenido dinámico.
        
        Args:
            driver: Instancia de WebDriver
            
        Returns:
            True si se detectó nuevo contenido, False si no hubo cambios
        """
        self.logger.info("Desplazando hacia abajo para cargar contenido dinámico")
        
        # Obtener altura inicial
        last_height = driver.execute_script("return document.body.scrollHeight")
        
        for i in range(self.max_scroll_attempts):
            # Desplazar hacia abajo
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            # Esperar a que cargue nuevo contenido
            time.sleep(self.scroll_pause)
            
            # Calcular nueva altura
            new_height = driver.execute_script("return document.body.scrollHeight")
            
            # Si la altura no cambió, hemos llegado al final
            if new_height == last_height:
                self.logger.info(f"Fin de la página alcanzado después de {i+1} scrolls")
                break
            
            last_height = new_height
        
        return True
    
    def _handle_iframes(self, driver: webdriver.Chrome) -> Dict[str, Any]:
        """
        Extrae contenido de todos los iframes en la página.
        
        Args:
            driver: Instancia de WebDriver
            
        Returns:
            Diccionario con contenido de iframes
        """
        if not self.handle_iframes:
            return {}
        
        iframe_contents = {}
        
        # Encontrar todos los iframes
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        
        for i, iframe in enumerate(iframes):
            try:
                iframe_url = iframe.get_attribute("src")
                if not iframe_url:
                    continue
                
                self.logger.info(f"Procesando iframe #{i+1}: {iframe_url}")
                
                # Cambiar al iframe
                driver.switch_to.frame(iframe)
                
                # Obtener contenido
                iframe_html = driver.page_source
                iframe_soup = BeautifulSoup(iframe_html, 'html.parser')
                
                # Extraer datos
                iframe_data = {
                    "url": iframe_url,
                    "text": self.text_extractor.extract(iframe_soup),
                    "images": self.image_extractor.extract(iframe_soup, base_url=iframe_url),
                    "links": self.link_extractor.extract(iframe_soup, base_url=iframe_url),
                    "html": iframe_html
                }
                
                iframe_contents[iframe_url] = iframe_data
                
                # Volver al contenido principal
                driver.switch_to.default_content()
                
            except Exception as e:
                self.logger.error(f"Error al procesar iframe: {str(e)}")
                driver.switch_to.default_content()
        
        return iframe_contents
    
    def _handle_shadow_dom(self, driver: webdriver.Chrome) -> Dict[str, Any]:
        """
        Extrae contenido de elementos Shadow DOM.
        
        Args:
            driver: Instancia de WebDriver
            
        Returns:
            Diccionario con contenido de Shadow DOM
        """
        if not self.handle_shadow_dom:
            return {}
        
        shadow_contents = {}
        
        # Ejecutar script para encontrar elementos con Shadow DOM
        shadow_hosts = driver.execute_script("""
            return Array.from(document.querySelectorAll('*')).filter(el => el.shadowRoot);
        """)
        
        for i, host in enumerate(shadow_hosts):
            try:
                host_id = host.get_attribute("id") or f"shadow-host-{i}"
                self.logger.info(f"Procesando Shadow DOM #{i+1}: {host_id}")
                
                # Obtener el contenido del Shadow DOM
                shadow_html = driver.execute_script("""
                    return arguments[0].shadowRoot.innerHTML;
                """, host)
                
                # Parsear y extraer datos
                shadow_soup = BeautifulSoup(f"<div>{shadow_html}</div>", 'html.parser')
                
                shadow_data = {
                    "id": host_id,
                    "text": self.text_extractor.extract(shadow_soup),
                    "images": self.image_extractor.extract(shadow_soup),
                    "links": self.link_extractor.extract(shadow_soup),
                    "html": shadow_html
                }
                
                shadow_contents[host_id] = shadow_data
                
            except Exception as e:
                self.logger.error(f"Error al procesar Shadow DOM: {str(e)}")
        
        return shadow_contents
    
    def _extract_xhr_data(self, driver: webdriver.Chrome) -> List[Dict[str, Any]]:
        """
        Captura solicitudes XHR y extrae datos JSON/API.
        
        Args:
            driver: Instancia de WebDriver
            
        Returns:
            Lista de datos extraídos de XHR
        """
        if not self.extract_xhr:
            return []
        
        # Instalar interceptor de red
        driver.execute_script("""
            window.xhrData = [];
            
            const originalXhrOpen = XMLHttpRequest.prototype.open;
            XMLHttpRequest.prototype.open = function() {
                this.addEventListener('load', function() {
                    try {
                        const url = this.responseURL;
                        const responseText = this.responseText;
                        let data;
                        
                        try {
                            data = JSON.parse(responseText);
                        } catch (e) {
                            data = responseText;
                        }
                        
                        window.xhrData.push({
                            url: url,
                            data: data,
                            timestamp: new Date().toISOString()});                    } catch (e) {
                        console.error('Error capturing XHR:', e);
                    }
                });
                originalXhrOpen.apply(this, arguments);
            };
        """)
                # Dar tiempo para que se procesen algunas solicitudes
        time.sleep(2)
        
        # Recuperar datos XHR capturados
        xhr_data = driver.execute_script("return window.xhrData;")
        
        # Procesar con el extractor API
        processed_data = self.api_extractor.process_xhr_data(xhr_data)
        
        return processed_data
    
    def _simulate_human_behavior(self, driver: webdriver.Chrome) -> None:
        """
        Simula comportamiento humano en la navegación.
        
        Args:
            driver: Instancia de WebDriver
        """
        if not self.simulate_human:
            return
        
        self.logger.info("Simulando comportamiento humano")
        
        try:
            # Movimientos aleatorios del mouse
            elements = driver.find_elements(By.CSS_SELECTOR, "a, button, input, select")
            if elements:
                for _ in range(random.randint(2, 5)):
                    element = random.choice(elements)
                    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                    time.sleep(random.uniform(0.5, 1.5))
            
            # Scroll aleatorio
            scroll_amount = random.randint(300, 700)
            driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            time.sleep(random.uniform(0.5, 2.0))
            
            # A veces volver arriba
            if random.random() < 0.3:
                driver.execute_script("window.scrollTo(0, 0);")
                time.sleep(random.uniform(0.5, 1.5))
                
        except Exception as e:
            self.logger.error(f"Error al simular comportamiento humano: {str(e)}")
    
    def scrape(self, url: str) -> Dict[str, Any]:
        """
        Realiza scraping dinámico de una URL utilizando Selenium.
        
        Args:
            url: URL objetivo
            
        Returns:
            Diccionario con datos extraídos
        """
        self.logger.info(f"Iniciando scraping dinámico en {url}")
        
        # Inicializar el driver en cada llamada para evitar problemas de estado
        driver = None
        
        for attempt in range(self.retry_attempts):
            try:
                # Configurar navegador
                driver = self._setup_browser()
                driver.set_page_load_timeout(self.load_timeout)
                
                # Abrir URL
                driver.get(url)
                
                # Esperar a que la página cargue completamente
                if self.wait_for_network_idle:
                    WebDriverWait(driver, self.load_timeout).until(
                        lambda d: d.execute_script('return document.readyState') == 'complete'
                    )
                
                # Simular comportamiento humano
                if self.simulate_human:
                    self._simulate_human_behavior(driver)
                
                # Desplazamiento para contenido infinito
                self._scroll_to_bottom(driver)
                
                # Obtener el contenido final de la página
                html_content = driver.page_source
                
                # Verificar captcha
                captcha_solution = self.handle_captcha(html_content)
                if captcha_solution:
                    # Implementar lógica para resolver captcha con Selenium
                    # (depende del tipo específico de captcha)
                    self.logger.info("Resolviendo captcha detectado")
                    # ... lógica específica de resolución captcha ...
                    
                    # Recargar página después de resolver
                    driver.refresh()
                    WebDriverWait(driver, self.load_timeout).until(
                        lambda d: d.execute_script('return document.readyState') == 'complete'
                    )
                    html_content = driver.page_source
                
                # Parsear HTML
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Extraer datos básicos
                result = {
                    "url": url,
                    "title": driver.title,
                    "text": self.text_extractor.extract(soup),
                    "images": self.image_extractor.extract(soup, base_url=url),
                    "links": self.link_extractor.extract(soup, base_url=url),
                    "videos": self.video_extractor.extract(soup, base_url=url),
                    "html": html_content,
                    "timestamp": self.request_manager.get_timestamp()
                }
                
                # Extraer datos avanzados
                result["iframes"] = self._handle_iframes(driver)
                result["shadow_dom"] = self._handle_shadow_dom(driver)
                result["xhr_data"] = self._extract_xhr_data(driver)
                
                # Capturar cookies y localStorage
                result["cookies"] = driver.get_cookies()
                result["local_storage"] = driver.execute_script(
                    "return Object.keys(localStorage).map(k => ({key: k, value: localStorage.getItem(k)}))"
                )
                
                # Cerrar navegador
                driver.quit()
                driver = None
                
                return result
                
            except Exception as e:
                self.logger.error(f"Error en intento {attempt+1}/{self.retry_attempts} para {url}: {str(e)}")
                
                if driver:
                    try:
                        driver.quit()
                    except:
                        pass
                    driver = None
                
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
        
        # No debería llegar aquí, pero por si acaso
        return {"url": url, "status": "failed", "error": "Unknown error", "timestamp": self.request_manager.get_timestamp()}