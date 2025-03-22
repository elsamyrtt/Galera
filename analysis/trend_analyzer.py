import pandas as pd
from typing import List, Dict, Any
from collections import Counter

class TrendAnalyzer:
    """
    Analiza tendencias en datos extraídos.
    """

    def __init__(self, data: List[Dict[str, Any]]):
        """
        Inicializa el analizador de tendencias con los datos proporcionados.

        Args:
            data: Lista de diccionarios con datos a analizar
        """
        self.data = data
        self.df = pd.DataFrame(data)

    def analyze_trends(self, date_column: str, value_column: str) -> Dict[str, Any]:
        """
        Analiza tendencias en los datos a lo largo del tiempo.

        Args:
            date_column: Nombre de la columna con fechas
            value_column: Nombre de la columna con valores a analizar

        Returns:
            Diccionario con análisis de tendencias
        """
        # Convertir la columna de fechas a tipo datetime
        self.df[date_column] = pd.to_datetime(self.df[date_column])

        # Agrupar por fecha y calcular la suma de valores
        trend_data = self.df.groupby(self.df[date_column].dt.date)[value_column].sum()

        # Calcular estadísticas básicas
        trend_stats = {
            "mean": trend_data.mean(),
            "median": trend_data.median(),
            "std_dev": trend_data.std(),
            "max": trend_data.max(),
            "min": trend_data.min()
        }

        return trend_stats

    def top_trends(self, text_column: str, n: int = 10) -> List[str]:
        """
        Identifica las tendencias más comunes en una columna de texto.

        Args:
            text_column: Nombre de la columna con texto a analizar
            n: Número de tendencias principales a devolver

        Returns:
            Lista de las tendencias más comunes
        """
        # Unir todo el texto en una sola cadena
        all_text = " ".join(self.df[text_column].dropna())

        # Contar la frecuencia de las palabras
        word_counts = Counter(all_text.split())

        # Obtener las n palabras más comunes
        top_words = word_counts.most_common(n)

        return [word for word, count in top_words]
