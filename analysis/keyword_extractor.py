from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
from typing import List, Dict, Any

class KeywordExtractor:
    """
    Extrae palabras clave y relaciones semánticas de los datos.
    """

    def __init__(self, data: List[Dict[str, Any]]):
        """
        Inicializa el extractor de palabras clave con los datos proporcionados.

        Args:
            data: Lista de diccionarios con datos a analizar
        """
        self.data = data
        self.df = pd.DataFrame(data)

    def extract_keywords(self, text_column: str, n: int = 10) -> List[str]:
        """
        Extrae palabras clave de una columna de texto utilizando TF-IDF.

        Args:
            text_column: Nombre de la columna con texto a analizar
            n: Número de palabras clave a devolver

        Returns:
            Lista de palabras clave
        """
        # Inicializar el vectorizador TF-IDF
        vectorizer = TfidfVectorizer(stop_words='english', max_features=n)

        # Ajustar y transformar el texto
        tfidf_matrix = vectorizer.fit_transform(self.df[text_column].dropna())

        # Obtener las palabras clave
        keywords = vectorizer.get_feature_names_out()

        return list(keywords)

    def semantic_relations(self, text_column: str) -> Dict[str, List[str]]:
        """
        Identifica relaciones semánticas entre palabras clave en una columna de texto.

        Args:
            text_column: Nombre de la columna con texto a analizar

        Returns:
            Diccionario con relaciones semánticas
        """
        # Extraer palabras clave
        keywords = self.extract_keywords(text_column, n=20)

        # Calcular co-ocurrencias de palabras clave
        co_occurrences = {}
        for text in self.df[text_column].dropna():
            words = set(text.split())
            for keyword in keywords:
                if keyword in words:
                    for other_word in words:
                        if other_word != keyword:
                            if keyword not in co_occurrences:
                                co_occurrences[keyword] = []
                            co_occurrences[keyword].append(other_word)

        return co_occurrences
