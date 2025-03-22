import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import numpy as np
from typing import List, Tuple, Any

class MLTrainer:
    """
    Entrenador de modelos de machine learning utilizando PyTorch.
    """

    def __init__(self, model: nn.Module, learning_rate: float = 0.001, epochs: int = 10):
        """
        Inicializa el entrenador con un modelo de PyTorch.

        Args:
            model: Modelo de PyTorch a entrenar
            learning_rate: Tasa de aprendizaje
            epochs: Número de épocas para entrenar
        """
        self.model = model
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.learning_rate)

    def train(self, data: List[Tuple[Any, int]]) -> None:
        """
        Entrena el modelo con los datos proporcionados.

        Args:
            data: Lista de tuplas con datos de entrada y etiquetas
        """
        # Dividir datos en entrenamiento y prueba
        train_data, test_data = train_test_split(data, test_size=0.2, random_state=42)

        # Preparar datos de entrenamiento
        train_loader = torch.utils.data.DataLoader(train_data, batch_size=32, shuffle=True)

        # Entrenar el modelo
        self.model.train()
        for epoch in range(self.epochs):
            for inputs, labels in train_loader:
                inputs, labels = inputs.to(self.device), labels.to(self.device)

                # Forward pass
                outputs = self.model(inputs)
                loss = self.criterion(outputs, labels)

                # Backward pass and optimization
                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()

            print(f"Epoch {epoch+1}/{self.epochs}, Loss: {loss.item()}")

    def evaluate(self, test_data: List[Tuple[Any, int]]) -> float:
        """
        Evalúa el modelo con datos de prueba.

        Args:
            test_data: Lista de tuplas con datos de entrada y etiquetas

        Returns:
            Precisión del modelo en los datos de prueba
        """
        self.model.eval()
        all_labels = []
        all_preds = []

        with torch.no_grad():
            for inputs, labels in test_data:
                inputs, labels = inputs.to(self.device), labels.to(self.device)
                outputs = self.model(inputs)
                _, preds = torch.max(outputs, 1)
                all_labels.append(labels.cpu().numpy())
                all_preds.append(preds.cpu().numpy())

        accuracy = accuracy_score(np.concatenate(all_labels), np.concatenate(all_preds))
        return accuracy

    def set_device(self, device: str = "cpu") -> None:
        """
        Establece el dispositivo para el entrenamiento (CPU o GPU).

        Args:
            device: Dispositivo a utilizar ("cpu" o "cuda")
        """
        self.device = torch.device(device if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
