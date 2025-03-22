import json
import os
from typing import List, Dict, Any

class JSONStorage:
    """
    Maneja el almacenamiento de datos en archivos JSON.
    """

    def __init__(self, file_path: str):
        """
        Inicializa el almacenamiento JSON.

        Args:
            file_path: Ruta al archivo JSON
        """
        self.file_path = file_path

    def save_data(self, data: List[Dict[str, Any]]) -> None:
        """
        Guarda datos en un archivo JSON.

        Args:
            data: Lista de diccionarios con datos a guardar
        """
        # Asegurarse de que el directorio exista
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

        # Escribir datos en el archivo JSON
        with open(self.file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def load_data(self) -> List[Dict[str, Any]]:
        """
        Carga datos desde un archivo JSON.

        Returns:
            Lista de diccionarios con datos cargados
        """
        if not os.path.exists(self.file_path):
            return []

        with open(self.file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
