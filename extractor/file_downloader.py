import requests
from typing import Optional

class FileDownloader:
    """
    Descargador de archivos como PDFs, CSVs, etc.
    """

    def download(self, url: str, destination: str) -> Optional[str]:
        """
        Descarga un archivo desde una URL y lo guarda en el destino especificado.

        Args:
            url: URL del archivo a descargar
            destination: Ruta de destino para guardar el archivo

        Returns:
            Ruta del archivo descargado o None si falla
        """
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            with open(destination, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            return destination
        except requests.RequestException as e:
            print(f"Error al descargar el archivo: {e}")
            return None
