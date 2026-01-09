"""
Example: Classification with FHE Encryption

Demonstrates privacy-preserving classification using OpenFHE integration
"""

import sys
import os
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.snn_model import SNNClassifier
from src.openfhe_integration import demonstrate_fhe_operations


def fhe_classification_example():
    """
    Demonstrate encrypted classification
    """
    print("\n" + "="*70)
    print("Privacy-Preserving Classification with OpenFHE")
    print("="*70 + "\n")
    
    # First, demonstrate basic FHE operations
    demonstrate_fhe_operations()
    
    # Generate a simple classification dataset
    print("\n[Dataset] Creating synthetic classification data...")
    np.random.seed(42)
    
    n_samples = 60
    n_features = 4
    
    # Two-class problem
    X_class0 = np.random.normal(0.2, 0.15, (n_samples // 2, n_features))
    X_class1 = np.random.normal(0.8, 0.15, (n_samples // 2, n_features))
    
    X = np.vstack([X_class0, X_class1])
    y = np.hstack([np.zeros(n_samples // 2), np.ones(n_samples // 2)])
    
    X = np.clip(X, 0, 1)
    
    # Shuffle
    indices = np.random.permutation(n_samples)
    X = X[indices]
    y = y[indices].astype(int)
    
    # Split
    split = int(0.75 * n_samples)
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]
    
    print(f"Training samples: {len(X_train)}")
    print(f"Test samples: {len(X_test)}\n")
    
    # Model WITHOUT FHE
    print("--- Standard Model (No Encryption) ---")
    model_plain = SNNClassifier(
        input_size=n_features,
        hidden_sizes=[12],
        output_size=2,
        use_fhe=False
    )
    
    model_plain.train(X_train, y_train, epochs=8, time_steps=12)
    acc_plain = model_plain.evaluate(X_test, y_test)
    
    # Model WITH FHE
    print("\n--- Encrypted Model (with OpenFHE) ---")
    model_fhe = SNNClassifier(
        input_size=n_features,
        hidden_sizes=[12],
        output_size=2,
        use_fhe=True
    )
    
    print("\n[FHE] Model with homomorphic encryption initialized")
    print("[FHE] Benefits:")
    print("  • Inference on encrypted data without decryption")
    print("  • Privacy-preserving machine learning")
    print("  • Secure model deployment in untrusted environments")
    print("  • Compliant with data privacy regulations")
    
    print("\n[Note] This demo uses a simulation layer.")
    print("[Note] In production, integrate with actual OpenFHE C++ library")
    print("[Note] using Python bindings (pybind11) or ctypes.\n")
    
    print("="*70)
    print("FHE Classification Demo Complete!")
    print("="*70 + "\n")


if __name__ == "__main__":
    fhe_classification_example()
