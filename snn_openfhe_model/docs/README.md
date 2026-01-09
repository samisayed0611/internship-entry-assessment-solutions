# SNN-based Machine Learning Model with OpenFHE and Software Acceleration

## Overview

This project implements a **Spiking Neural Network (SNN)** based machine learning model that integrates with the **OpenFHE** Fully Homomorphic Encryption (FHE) library and incorporates **software acceleration techniques**. The implementation enables privacy-preserving machine learning through encrypted inference while maintaining computational efficiency.

## Key Features

### 1. Spiking Neural Networks (SNN)
- **Leaky Integrate-and-Fire (LIF) Neuron Model**: Biologically-inspired neurons that accumulate input and fire spikes
- **Multi-layer Architecture**: Fully-connected SNN layers with configurable depth
- **Rate-based Encoding/Decoding**: Converts continuous values to spike trains and back
- **Temporal Dynamics**: Processes information over time steps, mimicking biological neural processing

### 2. OpenFHE Integration
- **FHE Simulation Layer**: Abstraction layer mimicking OpenFHE operations
- **Homomorphic Operations**: Add, multiply, and compute on encrypted data
- **CKKS Scheme Support**: Approximate arithmetic for real-valued computations
- **Privacy-Preserving Inference**: Classify encrypted data without decryption

### 3. Software Acceleration Techniques
- **Vectorization**: NumPy-based SIMD-like operations for parallel processing
- **Optimized Linear Algebra**: Leverages BLAS/LAPACK through NumPy
- **Batch Processing**: Efficient handling of multiple samples
- **Sparse Computation**: Only processes active neurons when beneficial

## Project Structure

```
snn_openfhe_model/
├── src/
│   ├── __init__.py              # Package initialization
│   ├── snn_neuron.py            # LIF neuron implementations
│   ├── openfhe_integration.py   # FHE operations and OpenFHE interface
│   ├── snn_layer.py             # SNN layer and network implementations
│   └── snn_model.py             # High-level classifier interface
├── examples/
│   ├── xor_example.py           # XOR problem demonstration
│   └── fhe_classification.py    # Encrypted classification demo
├── docs/
│   └── README.md                # This file
└── requirements.txt             # Python dependencies
```

## Installation

### Prerequisites

- Python 3.7+
- NumPy

### Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. For actual OpenFHE integration (C++ library):
```bash
# Install OpenFHE library
git clone https://github.com/openfheorg/openfhe-development.git
cd openfhe-development
mkdir build && cd build
cmake ..
make -j
sudo make install

# Install Python bindings (if available)
pip install openfhe-python
```

## Usage

### Basic Classification Example

```python
import numpy as np
from src.snn_model import SNNClassifier

# Create sample data
X_train = np.random.rand(100, 10)  # 100 samples, 10 features
y_train = np.random.randint(0, 2, 100)  # Binary classification

# Initialize classifier
model = SNNClassifier(
    input_size=10,
    hidden_sizes=[20, 20],
    output_size=2,
    use_fhe=False  # Set True for encrypted inference
)

# Train the model
model.train(X_train, y_train, epochs=10, time_steps=10)

# Make predictions
X_test = np.random.rand(20, 10)
predictions = model.predict(X_test)
```

### Using with FHE Encryption

```python
# Enable FHE for privacy-preserving inference
model = SNNClassifier(
    input_size=10,
    hidden_sizes=[20],
    output_size=2,
    use_fhe=True  # Enable homomorphic encryption
)

# Training typically done on plaintext
model.train(X_train, y_train, epochs=10)

# Inference can be done on encrypted data
# (In production, data would be encrypted client-side)
predictions = model.predict(X_test)
```

### Running Examples

```bash
# XOR problem
python examples/xor_example.py

# FHE classification demo
python examples/fhe_classification.py

# Main demonstration
python -m src.snn_model
```

## Technical Details

### Spiking Neural Network Architecture

The SNN uses the Leaky Integrate-and-Fire (LIF) neuron model:

```
dV/dt = -V/τ + I(t)
```

Where:
- `V`: Membrane potential
- `τ`: Time constant (related to leak_factor)
- `I(t)`: Input current at time t

When `V ≥ threshold`, the neuron fires a spike and resets.

### Software Acceleration

The implementation uses several acceleration techniques:

1. **Vectorization**: All neuron operations use NumPy's vectorized operations
   ```python
   # Instead of loops
   for i in range(n_neurons):
       membrane_potentials[i] = membrane_potentials[i] * leak + current[i]
   
   # Use vectorized operations (much faster)
   membrane_potentials = membrane_potentials * leak + currents
   ```

2. **Optimized Matrix Operations**: Weight computations use NumPy's BLAS-accelerated operations
   ```python
   # Synaptic current computation (vectorized)
   currents = weights.T @ input_spikes
   ```

3. **Batch Processing**: Multiple samples processed efficiently

### OpenFHE Integration

The current implementation provides a simulation layer that demonstrates the FHE workflow. To integrate with actual OpenFHE:

1. **Install OpenFHE C++ library** (see Installation section)

2. **Create Python bindings** using pybind11 or ctypes

3. **Replace FHESimulator** with actual OpenFHE calls:

```python
# Current (simulation)
fhe = FHESimulator(scheme="CKKS")
encrypted = fhe.encrypt(data)

# With real OpenFHE (pseudocode)
import openfhe
cc = openfhe.CryptoContextCKKS()
keys = cc.KeyGen()
encrypted = cc.Encrypt(keys.publicKey, data)
```

4. **Supported Operations**:
   - EvalAdd: Homomorphic addition
   - EvalMult: Homomorphic multiplication
   - EvalSum: Summation with rotations
   - Bootstrap: Refresh ciphertext noise

## Performance Considerations

### Software Acceleration Benefits

- **Vectorization**: 10-100x speedup over pure Python loops
- **NumPy BLAS**: Optimized C/Fortran implementations
- **Memory Efficiency**: Contiguous arrays, cache-friendly access

### FHE Performance Trade-offs

- **Encrypted Operations**: 100-1000x slower than plaintext
- **Noise Management**: Periodic bootstrapping required
- **Parameter Selection**: Balance between security and performance

### Optimization Strategies

1. **Reduce Network Depth**: Fewer layers = fewer encrypted operations
2. **Sparse Activations**: SNNs naturally sparse (only spiking neurons active)
3. **Batching**: Amortize encryption overhead
4. **Hybrid Approach**: Encrypt only sensitive layers

## Theoretical Background

### Why Spiking Neural Networks?

1. **Energy Efficiency**: Event-driven computation (only active on spikes)
2. **Temporal Processing**: Natural handling of time-series data
3. **Biological Plausibility**: Closer to brain computation
4. **Sparse Operations**: Fewer operations than dense ANNs

### Why Fully Homomorphic Encryption?

1. **Privacy Preservation**: Compute on encrypted data
2. **Secure Deployment**: Untrusted cloud servers can't see data
3. **Regulatory Compliance**: GDPR, HIPAA compliance
4. **Data Sovereignty**: Data never decrypted server-side

### SNN + FHE Synergy

- **Sparse Computations**: SNNs' sparsity reduces FHE overhead
- **Binary Operations**: Spike/no-spike easier to encrypt than real values
- **Event-driven**: Natural fit for encrypted stream processing

## Limitations and Future Work

### Current Limitations

1. **FHE Simulation**: Not using actual OpenFHE library (demonstration only)
2. **Simple Training**: Basic training loop (not full STDP or backprop)
3. **Small Networks**: Optimized for demonstration, not production scale

### Future Enhancements

1. **Real OpenFHE Integration**: Full C++ library integration
2. **Advanced Training**: Surrogate gradient descent, STDP learning
3. **Hardware Acceleration**: CUDA kernels for GPU acceleration
4. **Neuromorphic Hardware**: Integration with Loihi, SpiNNaker
5. **Optimized FHE Parameters**: Custom parameter selection for SNNs

## References

### Spiking Neural Networks
- Gerstner, W., & Kistler, W. M. (2002). Spiking Neuron Models
- Maass, W. (1997). Networks of spiking neurons: The third generation of neural network models

### Fully Homomorphic Encryption
- OpenFHE Documentation: https://openfhe.org/
- Brakerski, Z., & Vaikuntanathan, V. (2014). Efficient Fully Homomorphic Encryption from (Standard) LWE

### Privacy-Preserving Machine Learning
- Gilad-Bachrach, R., et al. (2016). CryptoNets: Applying Neural Networks to Encrypted Data

## License

This project is provided as an educational demonstration for the internship assessment.

## Author

Developed as part of the internship assessment solution demonstrating:
- Machine learning model development
- Cryptographic library integration
- Software optimization techniques
- Clean code and documentation practices
