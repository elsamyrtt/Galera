from elasticsearch import Elasticsearch, helpers
from typing import List, Dict, Any

class ElasticsearchStorage:
    """
    Maneja el almacenamiento de datos en Elasticsearch.
    """

    def __init__(self, hosts: List[str], index_name: str):
        """
        Inicializa el almacenamiento Elasticsearch.

        Args:
            hosts: Lista de hosts de Elasticsearch
            index_name: Nombre del índice
        """
        self.es = Elasticsearch(hosts)
        self.index_name = index_name
        self._create_index()

    def _create_index(self) -> None:
        """
        Crea el índice en Elasticsearch si no existe.
        """
        if not self.es.indices.exists(index=self.index_name):
            self.es.indices.create(index=self.index_name)

    def save_data(self, data: List[Dict[str, Any]]) -> None:
        """
        Guarda datos en Elasticsearch.

        Args:
            data: Lista de diccionarios con datos a guardar
        """
        actions = [
            {
                "_index": self.index_name,
                "_source": doc
            }
            for doc in data
        ]
        helpers.bulk(self.es, actions)

    def load_data(self) -> List[Dict[str, Any]]:
        """
        Carga datos desde Elasticsearch.

        Returns:
            Lista de diccionarios con datos cargados
        """
        response = self.es.search(index=self.index_name, body={"query": {"match_all": {}}})
        return [hit["_source"] for hit in response["hits"]["hits"]]
