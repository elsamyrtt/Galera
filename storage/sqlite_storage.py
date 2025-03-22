import sqlite3
from typing import List, Dict, Any

class SQLiteStorage:
    """
    Maneja el almacenamiento de datos en una base de datos SQLite.
    """

    def __init__(self, db_path: str):
        """
        Inicializa el almacenamiento SQLite.

        Args:
            db_path: Ruta a la base de datos SQLite
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self._create_table()

    def _create_table(self) -> None:
        """
        Crea la tabla para almacenar datos si no existe.
        """
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS scraped_data (
                    id INTEGER PRIMARY KEY,
                    url TEXT,
                    data TEXT
                )
            ''')

    def save_data(self, url: str, data: Dict[str, Any]) -> None:
        """
        Guarda datos en la base de datos SQLite.

        Args:
            url: URL asociada a los datos
            data: Diccionario con datos a guardar
        """
        with self.conn:
            self.conn.execute(
                'INSERT INTO scraped_data (url, data) VALUES (?, ?)',
                (url, json.dumps(data))
            )

    def load_data(self) -> List[Dict[str, Any]]:
        """
        Carga datos desde la base de datos SQLite.

        Returns:
            Lista de diccionarios con datos cargados
        """
        with self.conn:
            cursor = self.conn.execute('SELECT url, data FROM scraped_data')
            return [{"url": row[0], "data": json.loads(row[1])} for row in cursor]

    def close(self) -> None:
        """
        Cierra la conexión con la base de datos.
        """
        self.conn.close()
