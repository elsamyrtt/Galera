import json
from typing import List, Dict, Any

class ApiExtractor:
    """
    Extractor de datos JSON de APIs ocultas.
    """

    def process_xhr_data(self, xhr_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Procesa datos XHR capturados para extraer información útil.

        Args:
            xhr_data: Lista de datos XHR capturados

        Returns:
            Lista de diccionarios con datos procesados
        """
        processed_data = []
        for data in xhr_data:
            try:
                json_data = json.loads(data['data'])
                processed_data.append(json_data)
            except json.JSONDecodeError:
                # Si no se puede decodificar como JSON, se ignora
                continue
        return processed_data
