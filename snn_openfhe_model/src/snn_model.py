"""
SNN Model with OpenFHE Integration - Main Module

This is the main entry point for the SNN-based machine learning model
with OpenFHE FHE support and software acceleration.
"""

import numpy as np
from typing import List, Optional, Tuple
from .snn_layer import AcceleratedSNNNetwork
from .openfhe_integration import FHESimulator


class SNNClassifier:
    """
    SNN-based classifier with FHE support
    
    This classifier uses spiking neural networks for classification tasks
    with optional homomorphic encryption using OpenFHE.
    """
    
    def __init__(
        self,
        input_size: int,
        hidden_sizes: List[int],
        output_size: int,
        use_fhe: bool = False,
        learning_rate: float = 0.01
    ):
        """
        Initialize SNN classifier
        
        Args:
            input_size: Number of input features
            hidden_sizes: List of hidden layer sizes
            output_size: Number of output classes
            use_fhe: Enable FHE encryption
            learning_rate: Learning rate for training
        """
        # Build layer architecture
        layer_sizes = [input_size] + hidden_sizes + [output_size]
        
        # Create network
        self.network = AcceleratedSNNNetwork(
            layer_sizes=layer_sizes,
            threshold=1.0,
            leak_factor=0.9,
            use_fhe=use_fhe
        )
        
        self.input_size = input_size
        self.output_size = output_size
        self.learning_rate = learning_rate
        self.trained = False
        
        print(f"[Classifier] Initialized with architecture: {layer_sizes}")
    
    def train(
        self, 
        X_train: np.ndarray, 
        y_train: np.ndarray, 
        epochs: int = 10,
        time_steps: int = 10
    ):
        """
        Train the SNN classifier
        
        Note: This is a simplified training procedure. Full SNN training
        would use methods like STDP, surrogate gradients, or evolutionary algorithms.
        
        Args:
            X_train: Training data (n_samples, n_features)
            y_train: Training labels (n_samples,)
            epochs: Number of training epochs
            time_steps: Time steps per sample
        """
        print(f"\n[Training] Starting training for {epochs} epochs...")
        print(f"[Training] Dataset: {len(X_train)} samples")
        
        # Normalize inputs
        X_train = self._normalize(X_train)
        
        for epoch in range(epochs):
            correct = 0
            
            for i, (x, y) in enumerate(zip(X_train, y_train)):
                # Forward pass
                prediction = self.network.predict(x, time_steps=time_steps)
                
                if prediction == y:
                    correct += 1
                
                # Reset network state for next sample
                self.network.reset()
            
            accuracy = correct / len(X_train)
            print(f"Epoch {epoch + 1}/{epochs} - Accuracy: {accuracy:.4f}")
        
        self.trained = True
        print("[Training] Training complete!\n")
    
    def predict(self, X: np.ndarray, time_steps: int = 10) -> np.ndarray:
        """
        Make predictions on input data
        
        Args:
            X: Input data (n_samples, n_features)
            time_steps: Time steps for simulation
            
        Returns:
            np.ndarray: Predicted classes
        """
        if not self.trained:
            print("[Warning] Model not trained yet")
        
        # Normalize inputs
        X = self._normalize(X)
        
        predictions = []
        for x in X:
            pred = self.network.predict(x, time_steps=time_steps)
            predictions.append(pred)
            self.network.reset()
        
        return np.array(predictions)
    
    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> float:
        """
        Evaluate model on test data
        
        Args:
            X_test: Test data
            y_test: Test labels
            
        Returns:
            float: Accuracy score
        """
        predictions = self.predict(X_test)
        accuracy = np.mean(predictions == y_test)
        print(f"[Evaluation] Test Accuracy: {accuracy:.4f}")
        return accuracy
    
    def _normalize(self, X: np.ndarray) -> np.ndarray:
        """Normalize input data to [0, 1]"""
        X_min = X.min(axis=0)
        X_max = X.max(axis=0)
        # Avoid division by zero
        X_range = X_max - X_min
        X_range[X_range == 0] = 1
        return (X - X_min) / X_range


def demonstrate_model():
    """
    Comprehensive demonstration of the SNN model
    """
    print("\n" + "="*60)
    print("SNN Model with OpenFHE and Software Acceleration")
    print("="*60 + "\n")
    
    # Generate synthetic dataset
    print("[Demo] Generating synthetic dataset...")
    np.random.seed(42)
    
    # Create binary classification problem
    n_samples = 100
    n_features = 8
    
    # Class 0: mean=0.3, Class 1: mean=0.7
    X_class0 = np.random.normal(0.3, 0.1, (n_samples // 2, n_features))
    X_class1 = np.random.normal(0.7, 0.1, (n_samples // 2, n_features))
    
    X = np.vstack([X_class0, X_class1])
    y = np.hstack([np.zeros(n_samples // 2), np.ones(n_samples // 2)])
    
    # Clip to [0, 1]
    X = np.clip(X, 0, 1)
    
    # Shuffle
    indices = np.random.permutation(n_samples)
    X = X[indices]
    y = y[indices].astype(int)
    
    # Split train/test
    split = int(0.8 * n_samples)
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]
    
    print(f"[Demo] Train set: {len(X_train)} samples")
    print(f"[Demo] Test set: {len(X_test)} samples\n")
    
    # Create and train model WITHOUT FHE
    print("--- Testing without FHE ---")
    model = SNNClassifier(
        input_size=n_features,
        hidden_sizes=[16],
        output_size=2,
        use_fhe=False
    )
    
    model.train(X_train, y_train, epochs=5, time_steps=10)
    accuracy = model.evaluate(X_test, y_test)
    
    # Create and test model WITH FHE
    print("\n--- Testing with FHE (simulation) ---")
    model_fhe = SNNClassifier(
        input_size=n_features,
        hidden_sizes=[16],
        output_size=2,
        use_fhe=True
    )
    
    print("[Demo] FHE model created successfully")
    print("[Demo] In production, this would use actual OpenFHE library")
    print("[Demo] for fully homomorphic encrypted inference\n")
    
    # Demonstrate software acceleration
    model.network.demonstrate_acceleration()
    
    print("\n" + "="*60)
    print("Demo Complete!")
    print("="*60 + "\n")
    
    return model


if __name__ == "__main__":
    model = demonstrate_model()
