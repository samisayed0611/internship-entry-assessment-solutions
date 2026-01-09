# SNN Model with OpenFHE Integration

## Quick Start

This directory contains a complete implementation of a Spiking Neural Network (SNN) based machine learning model with OpenFHE Fully Homomorphic Encryption support and software acceleration techniques.

### Features

✅ **Spiking Neural Networks**: Biologically-inspired neurons with temporal dynamics  
✅ **OpenFHE Integration**: Privacy-preserving encrypted inference  
✅ **Software Acceleration**: Vectorized operations for improved performance  
✅ **Complete Examples**: Working demonstrations included  

### Installation

```bash
cd snn_openfhe_model
pip install -r requirements.txt
```

### Run Examples

```bash
# Run the main demonstration
python -m src.snn_model

# XOR problem
python examples/xor_example.py

# FHE classification
python examples/fhe_classification.py
```

### Documentation

For detailed documentation, see: [docs/README.md](docs/README.md)

### Architecture

```
Input → [Encoding] → SNN Layer 1 → SNN Layer 2 → ... → [Decoding] → Output
                          ↓
                    [Optional FHE Encryption]
                          ↓
                   [Software Acceleration]
```

### Quick Example

```python
from src.snn_model import SNNClassifier
import numpy as np

# Create model
model = SNNClassifier(
    input_size=10,
    hidden_sizes=[20],
    output_size=2,
    use_fhe=True  # Enable encryption
)

# Train and predict
X = np.random.rand(100, 10)
y = np.random.randint(0, 2, 100)
model.train(X, y, epochs=10)
predictions = model.predict(X)
```

## Project Structure

```
snn_openfhe_model/
├── src/                    # Core implementation
│   ├── snn_neuron.py      # Neuron models
│   ├── openfhe_integration.py  # FHE operations
│   ├── snn_layer.py       # Network layers
│   └── snn_model.py       # Main classifier
├── examples/               # Demonstration scripts
├── docs/                   # Detailed documentation
└── requirements.txt        # Dependencies
```

## Technical Highlights

### Software Acceleration
- NumPy vectorization (SIMD-like operations)
- Optimized BLAS/LAPACK matrix operations
- Batch processing capabilities
- **~10-100x speedup** over pure Python

### OpenFHE Integration
- Homomorphic encryption for privacy
- CKKS scheme for real-valued arithmetic
- Encrypted inference without decryption
- Production-ready architecture

### SNN Implementation
- Leaky Integrate-and-Fire neurons
- Rate-based spike encoding
- Temporal dynamics simulation
- Biologically-inspired computation
