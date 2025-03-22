import csv
import os
from typing import List, Dict, Any

class CSVStorage:
    """
    Maneja el almacenamiento de datos en archivos CSV.
    """

    def __init__(self, file_path: str):
        """
        Inicializa el almacenamiento CSV.

        Args:
            file_path: Ruta al archivo CSV
        """
        self.file_path = file_path

    def save_data(self, data: List[Dict[str, Any]]) -> None:
        """
        Guarda datos en un archivo CSV.

        Args:
            data: Lista de diccionarios con datos a guardar
        """
        # Asegurarse de que el directorio exista
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

        # Escribir datos en el archivo CSV
        with open(self.file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)

    def load_data(self) -> List[Dict[str, Any]]:
        """
        Carga datos desde un archivo CSV.

        Returns:
            Lista de diccionarios con datos cargados
        """
        if not os.path.exists(self.file_path):
            return []

        with open(self.file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            return list(reader)
