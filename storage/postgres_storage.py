import psycopg2
from typing import List, Dict, Any
import json

class PostgresStorage:
    """
    Maneja el almacenamiento de datos en una base de datos PostgreSQL.
    """

    def __init__(self, db_config: Dict[str, str]):
        """
        Inicializa el almacenamiento PostgreSQL.

        Args:
            db_config: Configuración de la base de datos (host, dbname, user, password)
        """
        self.conn = psycopg2.connect(**db_config)
        self._create_table()

    def _create_table(self) -> None:
        """
        Crea la tabla para almacenar datos si no existe.
        """
        with self.conn.cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scraped_data (
                    id SERIAL PRIMARY KEY,
                    url TEXT,
                    data JSONB
                )
            ''')
            self.conn.commit()

    def save_data(self, url: str, data: Dict[str, Any]) -> None:
        """
        Guarda datos en la base de datos PostgreSQL.

        Args:
            url: URL asociada a los datos
            data: Diccionario con datos a guardar
        """
        with self.conn.cursor() as cursor:
            cursor.execute(
                'INSERT INTO scraped_data (url, data) VALUES (%s, %s)',
                (url, json.dumps(data))
            )
            self.conn.commit()

    def load_data(self) -> List[Dict[str, Any]]:
        """
        Carga datos desde la base de datos PostgreSQL.

        Returns:
            Lista de diccionarios con datos cargados
        """
        with self.conn.cursor() as cursor:
            cursor.execute('SELECT url, data FROM scraped_data')
            return [{"url": row[0], "data": row[1]} for row in cursor.fetchall()]

    def close(self) -> None:
        """
        Cierra la conexión con la base de datos.
        """
        self.conn.close()
