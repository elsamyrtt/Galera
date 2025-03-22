# galera/utils/captcha_solver.py
import logging
import time
import base64
import re
import random
from typing import Optional, Dict, Any, Union
from PIL import Image
from pytesseract import image_to_string
import io
import requests

class CaptchaSolver:
    """
    Resuelve diversos tipos de CAPTCHAs utilizando servicios externos o técnicas locales.
    """
    
    def __init__(
        self,
        service: str = "local",
        api_key: Optional[str] = None,
        api_url: Optional[str] = None,
        timeout: int = 60,
        max_attempts: int = 3,
        delay_between_attempts: tuple = (2, 5)
    ):
        """
        Inicializa el solucionador de CAPTCHAs.
        
        Args:
            service: Servicio a utilizar ("local", "2captcha", "anticaptcha", etc.)
            api_key: Clave API para el servicio externo
            api_url: URL de API personalizada
            timeout: Tiempo máximo de espera para resolución
            max_attempts: Número máximo de intentos
            delay_between_attempts: Rango de tiempo (min, max) entre intentos
        """
        self.logger = logging.getLogger("galera.CaptchaSolver")
        
        self.service = service.lower()
        self.api_key = api_key
        self.api_url = api_url
        self.timeout = timeout
        self.max_attempts = max_attempts
        self.delay_between_attempts = delay_between_attempts
        
        # Validar configuración
        if self.service != "local" and not self.api_key:
            self.logger.warning("Servicio de CAPTCHA externo configurado sin API key")
    
    def solve(self, html_content: str) -> Optional[str]:
        """
        Detecta y resuelve CAPTCHAs en el contenido HTML.
        
        Args:
            html_content: Contenido HTML que puede contener CAPTCHA
            
        Returns:
            Solución al CAPTCHA o None si no se encuentra
        """
        # Detectar tipo de CAPTCHA
        captcha_type = self._detect_captcha(html_content)
        
        if not captcha_type:
            return None
        
        self.logger.info(f"CAPTCHA detectado de tipo: {captcha_type}")
        
        # Resolver según el tipo
        for attempt in range(self.max_attempts):
            try:
                if captcha_type == "recaptcha_v2":
                    return self._solve_recaptcha_v2(html_content)
                elif captcha_type == "recaptcha_v3":
                    return self._solve_recaptcha_v3(html_content)
                elif captcha_type == "image_captcha":
                    return self._solve_image_captcha(html_content)
                elif captcha_type == "text_captcha":
                    return self._solve_text_captcha(html_content)
                elif captcha_type == "hcaptcha":
                    return self._solve_hcaptcha(html_content)
                else:
                    self.logger.warning(f"Tipo de CAPTCHA no soportado: {captcha_type}")
                    return None
            
            except Exception as e:
                self.logger.error(f"Error al resolver CAPTCHA (intento {attempt+1}): {str(e)}")
                
                if attempt < self.max_attempts - 1:
                    delay = random.uniform(
                        self.delay_between_attempts[0],
                        self.delay_between_attempts[1]
                    )
                    time.sleep(delay)
        
        return None
    
    def _detect_captcha(self, html_content: str) -> Optional[str]:
        """
        Detecta el tipo de CAPTCHA presente en el HTML.
        
        Args:
            html_content: Contenido HTML
            
        Returns:
            Tipo de CAPTCHA o None si no se detecta
        """
        content_lower = html_content.lower()
        
        # ReCAPTCHA v2
        if "g-recaptcha" in content_lower or "google.com/recaptcha/api.js" in content_lower:
            return "recaptcha_v2"
        
        # ReCAPTCHA v3
        if "recaptcha/api.js?render=" in content_lower:
            return "recaptcha_v3"
        
        # hCaptcha
        if "hcaptcha.com/captcha" in content_lower:
            return "hcaptcha"
        
        # Captcha de imagen (basado en patrones comunes)
        img_patterns = [
            r'<img[^>]*captcha[^>]*>',
            r'<img[^>]*src="[^"]*captcha[^"]*"[^>]*>',
            r'<img[^>]*src="[^"]*verify[^"]*"[^>]*>'
        ]
        
        for pattern in img_patterns:
            if re.search(pattern, content_lower):
                return "image_captcha"
        
        # Captcha de texto (preguntas simples)
        text_patterns = [
            r'what is \d+\s*[+]\s*\d+',
            r'solve this: \d+\s*[+*/-]\s*\d+',
            r'captcha.*?\?.*?input'
        ]
        
        for pattern in text_patterns:
            if re.search(pattern, content_lower):
                return "text_captcha"
        
        return None
    
    def _solve_recaptcha_v2(self, html_content: str) -> Optional[str]:
        """
        Resuelve ReCAPTCHA v2.
        
        Args:
            html_content: Contenido HTML con ReCAPTCHA
            
        Returns:
            Token de solución
        """
        if self.service == "local":
            self.logger.warning("ReCAPTCHA v2 no puede resolverse localmente")
            return None
        
        # Extraer site key
        site_key_match = re.search(r'data-sitekey="([^"]+)"', html_content)
        if not site_key_match:
            self.logger.error("No se pudo encontrar la site key de ReCAPTCHA")
            return None
        
        site_key = site_key_match.group(1)
        
        # Extraer URL de la página
        page_url_match = re.search(r'<link[^>]*rel="canonical"[^>]*href="([^"]+)"', html_content)
        page_url = page_url_match.group(1) if page_url_match else "https://example.com"
        
        if self.service == "2captcha":
            return self._solve_with_2captcha("recaptcha_v2", {
                "googlekey": site_key,
                "pageurl": page_url
            })
        
        # Otros servicios...
        
        return None
    
    def _solve_recaptcha_v3(self, html_content: str) -> Optional[str]:
        """
        Resuelve ReCAPTCHA v3.
        
        Args:
            html_content: Contenido HTML con ReCAPTCHA
            
        Returns:
            Token de solución
        """
        # Similar a v2 pero con diferente extracción de parámetros
        # ReCAPTCHA v3 suele requerir action y puntuaciones
        
        if self.service == "local":
            self.logger.warning("ReCAPTCHA v3 no puede resolverse localmente")
            return None
        
        # Extraer site key (formato diferente en v3)
        site_key_match = re.search(r'recaptcha/api.js\?render=([^"&]+)', html_content)
        if not site_key_match:
            self.logger.error("No se pudo encontrar la site key de ReCAPTCHA v3")
            return None
        
        site_key = site_key_match.group(1)
        
        # Extraer action si está disponible
        action_match = re.search(r'execute\([^,]+,\s*{action:\s*[\'"]([^\'"]+)', html_content)
        action = action_match.group(1) if action_match else "verify"
        
        # Extraer URL de la página
        page_url_match = re.search(r'<link[^>]*rel="canonical"[^>]*href="([^"]+)"', html_content)
        page_url = page_url_match.group(1) if page_url_match else "https://example.com"
        
        if self.service == "2captcha":
            return self._solve_with_2captcha("recaptcha_v3", {
                "googlekey": site_key,
                "pageurl": page_url,
                "action": action,
                "min_score": 0.7
            })
        
        # Otros servicios...
        
        return None
    
    def _solve_image_captcha(self, html_content: str) -> Optional[str]:
        """
        Resuelve CAPTCHA de imagen.
        
        Args:
            html_content: Contenido HTML con CAPTCHA de imagen
            
        Returns:
            Texto reconocido de la imagen
        """
        # Extraer URL de la imagen
        img_match = re.search(r'<img[^>]*src="([^"]*captcha[^"]*)"[^>]*>', html_content)
        if not img_match:
            self.logger.error("No se pudo encontrar la URL de la imagen CAPTCHA")
            return None

        img_url = img_match.group(1)

        # Descargar la imagen
        try:
            response = requests.get(img_url, timeout=10)
            response.raise_for_status()
            img_data = response.content
        except Exception as e:
            self.logger.error(f"Error al descargar la imagen CAPTCHA: {str(e)}")
            return None

        # Resolver imagen CAPTCHA
        if self.service == "local":
            return self._solve_image_locally(img_data)
        elif self.service == "2captcha":
            return self._solve_with_2captcha("image", {"body": base64.b64encode(img_data).decode("utf-8")})
        # Otros servicios...

        return None

    def _solve_image_locally(self, img_data: bytes) -> Optional[str]:
        """
        Resuelve una imagen CAPTCHA localmente utilizando OCR.

        Args:
            img_data: Datos de la imagen en bytes

        Returns:
            Texto reconocido de la imagen
        """
        try:
            img = Image.open(io.BytesIO(img_data))
            text = image_to_string(img)
            return text.strip()
        except Exception as e:
            self.logger.error(f"Error al resolver imagen CAPTCHA localmente: {str(e)}")
            return None

    def _solve_text_captcha(self, html_content: str) -> Optional[str]:
        """
        Resuelve CAPTCHA de texto (preguntas simples).

        Args:
            html_content: Contenido HTML con CAPTCHA de texto

        Returns:
            Respuesta al CAPTCHA
        """
        # Extraer pregunta del CAPTCHA
        question_match = re.search(r'what is (\d+)\s*([+*/-])\s*(\d+)', html_content.lower())
        if not question_match:
            self.logger.error("No se pudo encontrar la pregunta del CAPTCHA de texto")
            return None

        num1, operator, num2 = question_match.groups()
        num1, num2 = int(num1), int(num2)

        # Calcular respuesta
        if operator == '+':
            answer = num1 + num2
        elif operator == '-':
            answer = num1 - num2
        elif operator == '*':
            answer = num1 * num2
        elif operator == '/':
            answer = num1 / num2
        else:
            self.logger.error(f"Operador no soportado: {operator}")
            return None

        return str(answer)

    def _solve_hcaptcha(self, html_content: str) -> Optional[str]:
        """
        Resuelve hCaptcha.

        Args:
            html_content: Contenido HTML con hCaptcha

        Returns:
            Token de solución
        """
        if self.service == "local":
            self.logger.warning("hCaptcha no puede resolverse localmente")
            return None

        # Extraer site key
        site_key_match = re.search(r'data-sitekey="([^"]+)"', html_content)
        if not site_key_match:
            self.logger.error("No se pudo encontrar la site key de hCaptcha")
            return None

        site_key = site_key_match.group(1)

        # Extraer URL de la página
        page_url_match = re.search(r'<link[^>]*rel="canonical"[^>]*href="([^"]+)"', html_content)
        page_url = page_url_match.group(1) if page_url_match else "https://example.com"

        if self.service == "2captcha":
            return self._solve_with_2captcha("hcaptcha", {
                "sitekey": site_key,
                "pageurl": page_url
            })

        # Otros servicios...

        return None

    def _solve_with_2captcha(self, captcha_type: str, params: Dict[str, Any]) -> Optional[str]:
        """
        Resuelve CAPTCHA utilizando el servicio 2captcha.

        Args:
            captcha_type: Tipo de CAPTCHA ("recaptcha_v2", "recaptcha_v3", "hcaptcha", "image")
            params: Parámetros específicos para el tipo de CAPTCHA

        Returns:
            Token de solución
        """
        try:
            # Enviar solicitud de resolución
            response = requests.post(
                f"http://2captcha.com/in.php",
                data={
                    "key": self.api_key,
                    "method": "userrecaptcha",
                    "json": 1,
                    **params
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            result = response.json()

            if result["status"] == 1:
                request_id = result["request"]

                # Esperar a que se resuelva
                for _ in range(self.timeout // 5):
                    time.sleep(5)
                    response = requests.get(
                        f"http://2captcha.com/res.php",
                        params={
                            "key": self.api_key,
                            "action": "get",
                            "id": request_id,
                            "json": 1
                        },
                        timeout=self.timeout
                    )
                    response.raise_for_status()
                    result = response.json()

                    if result["status"] == 1:
                        return result["request"]

            self.logger.error(f"Error al resolver CAPTCHA con 2captcha: {result.get('request', 'Unknown error')}")

        except Exception as e:
            self.logger.error(f"Error al resolver CAPTCHA con 2captcha: {str(e)}")

        return None
