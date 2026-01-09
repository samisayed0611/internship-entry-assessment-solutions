"""
Example: XOR Problem with SNN and OpenFHE

This example demonstrates solving the XOR problem using the SNN model
with optional FHE encryption.
"""

import sys
import os
import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.snn_model import SNNClassifier


def xor_example():
    """
    Solve XOR problem using SNN
    
    XOR is a classic non-linearly separable problem that requires
    at least one hidden layer to solve.
    """
    print("\n" + "="*60)
    print("XOR Problem with SNN")
    print("="*60 + "\n")
    
    # XOR dataset
    X_train = np.array([
        [0.0, 0.0],
        [0.0, 1.0],
        [1.0, 0.0],
        [1.0, 1.0]
    ])
    
    y_train = np.array([0, 1, 1, 0])
    
    print("XOR Truth Table:")
    print("Input | Output")
    print("------|-------")
    for i, (x, y) in enumerate(zip(X_train, y_train)):
        print(f"{x}  |  {y}")
    print()
    
    # Create SNN classifier
    model = SNNClassifier(
        input_size=2,
        hidden_sizes=[8, 8],  # Two hidden layers for XOR
        output_size=2,
        use_fhe=False
    )
    
    # Train the model (multiple epochs to learn XOR)
    print("\n[Training] Learning XOR pattern...")
    model.train(X_train, y_train, epochs=20, time_steps=15)
    
    # Test predictions
    print("\n[Testing] Making predictions...")
    predictions = model.predict(X_train, time_steps=15)
    
    print("\nResults:")
    print("Input     | True | Predicted")
    print("----------|------|----------")
    for x, y_true, y_pred in zip(X_train, y_train, predictions):
        status = "✓" if y_true == y_pred else "✗"
        print(f"{x} | {y_true}    | {y_pred}         {status}")
    
    accuracy = np.mean(predictions == y_train)
    print(f"\nFinal Accuracy: {accuracy * 100:.1f}%")
    
    print("\n" + "="*60)
    print("XOR Example Complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    np.random.seed(42)
    xor_example()
