import spacy
from typing import List, Dict, Any

class NLPProcessor:
    """
    Procesador de lenguaje natural utilizando spaCy.
    """

    def __init__(self, model: str = "en_core_web_sm"):
        """
        Inicializa el procesador NLP con un modelo de spaCy.

        Args:
            model: Nombre del modelo de spaCy a utilizar
        """
        self.nlp = spacy.load(model)

    def process_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Procesa el texto para extraer entidades nombradas y relaciones.

        Args:
            text: Texto a procesar

        Returns:
            Lista de entidades nombradas y sus relaciones
        """
        doc = self.nlp(text)
        entities = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]
        return entities

    def similarity(self, text1: str, text2: str) -> float:
        """
        Calcula la similitud entre dos textos.

        Args:
            text1: Primer texto
            text2: Segundo texto

        Returns:
            Similitud entre los dos textos
        """
        doc1 = self.nlp(text1)
        doc2 = self.nlp(text2)
        return doc1.similarity(doc2)
