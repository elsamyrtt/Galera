import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from typing import List, Dict, Any

class DataVisualizer:
    """
    Visualiza datos utilizando Matplotlib y Seaborn.
    """

    def __init__(self, data: List[Dict[str, Any]]):
        """
        Inicializa el visualizador de datos con los datos proporcionados.

        Args:
            data: Lista de diccionarios con datos a visualizar
        """
        self.data = data
        self.df = pd.DataFrame(data)

    def plot_trends(self, date_column: str, value_column: str) -> None:
        """
        Grafica las tendencias de los datos a lo largo del tiempo.

        Args:
            date_column: Nombre de la columna con fechas
            value_column: Nombre de la columna con valores a graficar
        """
        # Convertir la columna de fechas a tipo datetime
        self.df[date_column] = pd.to_datetime(self.df[date_column])

        # Graficar las tendencias
        plt.figure(figsize=(10, 6))
        sns.lineplot(data=self.df, x=date_column, y=value_column)
        plt.title(f'Tendencias en {value_column} a lo largo del tiempo')
        plt.xlabel('Fecha')
        plt.ylabel(value_column)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    def plot_keyword_frequency(self, keywords: List[str], text_column: str) -> None:
        """
        Grafica la frecuencia de palabras clave en una columna de texto.

        Args:
            keywords: Lista de palabras clave a graficar
            text_column: Nombre de la columna con texto a analizar
        """
        # Contar la frecuencia de las palabras clave
        keyword_counts = {keyword: 0 for keyword in keywords}
        for text in self.df[text_column].dropna():
            words = text.split()
            for keyword in keywords:
                if keyword in words:
                    keyword_counts[keyword] += 1

        # Graficar la frecuencia de palabras clave
        plt.figure(figsize=(10, 6))
        sns.barplot(x=list(keyword_counts.keys()), y=list(keyword_counts.values()))
        plt.title('Frecuencia de Palabras Clave')
        plt.xlabel('Palabras Clave')
        plt.ylabel('Frecuencia')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
