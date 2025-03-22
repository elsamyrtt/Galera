from pymongo import MongoClient
from typing import List, Dict, Any

class MongoStorage:
    """
    Maneja el almacenamiento de datos en una base de datos MongoDB.
    """

    def __init__(self, uri: str, db_name: str, collection_name: str):
        """
        Inicializa el almacenamiento MongoDB.

        Args:
            uri: URI de conexión a MongoDB
            db_name: Nombre de la base de datos
            collection_name: Nombre de la colección
        """
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def save_data(self, data: Dict[str, Any]) -> None:
        """
        Guarda datos en la base de datos MongoDB.

        Args:
            data: Diccionario con datos a guardar
        """
        self.collection.insert_one(data)

    def save_multiple(self, data_list: List[Dict[str, Any]]) -> None:
        """
        Guarda múltiples documentos en la base de datos MongoDB.

        Args:
            data_list: Lista de diccionarios con datos a guardar
        """
        if data_list:
            self.collection.insert_many(data_list)

    def load_data(self, query: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Carga datos desde la base de datos MongoDB.

        Args:
            query: Consulta para filtrar los datos a cargar

        Returns:
            Lista de diccionarios con datos cargados
        """
        if query is None:
            query = {}
        return list(self.collection.find(query))

    def update_data(self, query: Dict[str, Any], new_values: Dict[str, Any]) -> None:
        """
        Actualiza datos en la base de datos MongoDB.

        Args:
            query: Consulta para encontrar los documentos a actualizar
            new_values: Nuevos valores a establecer en los documentos encontrados
        """
        self.collection.update_many(query, {"$set": new_values})

    def delete_data(self, query: Dict[str, Any]) -> None:
        """
        Elimina datos de la base de datos MongoDB.

        Args:
            query: Consulta para encontrar los documentos a eliminar
        """
        self.collection.delete_many(query)

    def close(self) -> None:
        """
        Cierra la conexión con la base de datos.
        """
        self.client.close()
