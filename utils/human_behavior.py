import logging
import random
import time
from typing import Optional

class HumanBehaviorSimulator:
    """
    Simula comportamiento humano para evitar detección como bot.
    """

    def __init__(
        self,
        min_pause: float = 0.5,
        max_pause: float = 2.0,
        mouse_movements: bool = True,
        scroll_behavior: bool = True,
        random_clicks: bool = True,
        typing_speed: tuple = (0.1, 0.3)
    ):
        """
        Inicializa el simulador de comportamiento humano.

        Args:
            min_pause: Pausa mínima entre acciones (segundos)
            max_pause: Pausa máxima entre acciones (segundos)
            mouse_movements: Si se deben simular movimientos del mouse
            scroll_behavior: Si se debe simular desplazamiento
            random_clicks: Si se deben simular clics aleatorios
            typing_speed: Velocidad de escritura (min, max) caracteres por segundo
        """
        self.logger = logging.getLogger("galera.HumanBehaviorSimulator")

        self.min_pause = min_pause
        self.max_pause = max_pause
        self.mouse_movements = mouse_movements
        self.scroll_behavior = scroll_behavior
        self.random_clicks = random_clicks
        self.typing_speed = typing_speed

    def simulate(self, driver) -> None:
        """
        Simula comportamiento humano en el navegador.

        Args:
            driver: Instancia de WebDriver
        """
        self.logger.info("Simulando comportamiento humano")

        # Pausa inicial
        self._random_pause()

        if self.mouse_movements:
            self._simulate_mouse_movements(driver)

        if self.scroll_behavior:
            self._simulate_scrolling(driver)

        if self.random_clicks:
            self._simulate_random_clicks(driver)

    def _random_pause(self) -> None:
        """
        Introduce una pausa aleatoria para simular comportamiento humano.
        """
        pause_duration = random.uniform(self.min_pause, self.max_pause)
        time.sleep(pause_duration)

    def _simulate_mouse_movements(self, driver) -> None:
        """
        Simula movimientos del mouse.

        Args:
            driver: Instancia de WebDriver
        """
        try:
            elements = driver.find_elements_by_css_selector("a, button, input, select")
            if elements:
                for _ in range(random.randint(2, 5)):
                    element = random.choice(elements)
                    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                    self._random_pause()
        except Exception as e:
            self.logger.error(f"Error al simular movimientos del mouse: {str(e)}")

    def _simulate_scrolling(self, driver) -> None:
        """
        Simula desplazamiento en la página.

        Args:
            driver: Instancia de WebDriver
        """
        try:
            scroll_amount = random.randint(300, 700)
            driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            self._random_pause()

            # A veces volver arriba
            if random.random() < 0.3:
                driver.execute_script("window.scrollTo(0, 0);")
                self._random_pause()
        except Exception as e:
            self.logger.error(f"Error al simular desplazamiento: {str(e)}")

    def _simulate_random_clicks(self, driver) -> None:
        """
        Simula clics aleatorios en la página.

        Args:
            driver: Instancia de WebDriver
        """
        try:
            elements = driver.find_elements_by_css_selector("a, button")
            if elements:
                for _ in range(random.randint(1, 3)):
                    element = random.choice(elements)
                    element.click()
                    self._random_pause()
        except Exception as e:
            self.logger.error(f"Error al simular clics aleatorios: {str(e)}")

    def type_text(self, driver, element, text: str) -> None:
        """
        Simula la escritura de texto con velocidad humana.

        Args:
            driver: Instancia de WebDriver
            element: Elemento web donde escribir
            text: Texto a escribir
        """
        try:
            for char in text:
                element.send_keys(char)
                time.sleep(random.uniform(self.typing_speed[0], self.typing_speed[1]))
        except Exception as e:
            self.logger.error(f"Error al simular escritura de texto: {str(e)}")
