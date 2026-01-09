"""
SNN Model with OpenFHE Integration

A Spiking Neural Network (SNN) implementation with:
- OpenFHE Fully Homomorphic Encryption support
- Software acceleration using vectorization
- Privacy-preserving machine learning capabilities
"""

from .snn_neuron import LIFNeuron, VectorizedLIFNeurons
from .openfhe_integration import FHESimulator, EncryptedArray, FHECompatibleWeights
from .snn_layer import SNNLayer, AcceleratedSNNNetwork
from .snn_model import SNNClassifier, demonstrate_model

__version__ = "1.0.0"
__all__ = [
    "LIFNeuron",
    "VectorizedLIFNeurons",
    "FHESimulator",
    "EncryptedArray",
    "FHECompatibleWeights",
    "SNNLayer",
    "AcceleratedSNNNetwork",
    "SNNClassifier",
    "demonstrate_model"
]
