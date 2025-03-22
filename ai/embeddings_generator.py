from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Any

class EmbeddingsGenerator:
    """
    Generador de embeddings para representar texto.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Inicializa el generador de embeddings con un modelo de SentenceTransformer.

        Args:
            model_name: Nombre del modelo de SentenceTransformer a utilizar
        """
        self.model = SentenceTransformer(model_name)

    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Genera embeddings para una lista de textos.

        Args:
            texts: Lista de textos para generar embeddings

        Returns:
            Matriz de embeddings
        """
        embeddings = self.model.encode(texts)
        return embeddings

    def embeddings_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calcula la similitud entre dos embeddings.

        Args:
            embedding1: Primer embedding
            embedding2: Segundo embedding

        Returns:
            Similitud entre los dos embeddings
        """
        similarity = np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))
        return similarity
