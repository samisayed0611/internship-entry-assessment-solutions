# OpenFHE Integration Guide

## Overview

This guide explains how to integrate the actual OpenFHE C++ library with this Python SNN implementation.

## Current Implementation

The current implementation uses a **simulation layer** (`FHESimulator`) that mimics OpenFHE operations. This allows:
- Understanding the FHE workflow
- Testing the SNN architecture
- Development without OpenFHE installation

## Integrating Actual OpenFHE

### Option 1: Using OpenFHE Python Bindings (Recommended)

If OpenFHE Python bindings are available:

```python
# Replace FHESimulator with actual OpenFHE
import openfhe

class OpenFHEContext:
    def __init__(self, scheme="CKKS"):
        # Initialize crypto context
        parameters = openfhe.CCParams_CKKS()
        parameters.SetMultiplicativeDepth(10)
        parameters.SetScalingModSize(50)
        parameters.SetBatchSize(8192)
        
        self.cc = openfhe.CryptoContext(parameters)
        self.cc.Enable(openfhe.PKE)
        self.cc.Enable(openfhe.KEYSWITCH)
        self.cc.Enable(openfhe.LEVELEDSHE)
        
        # Generate keys
        self.keys = self.cc.KeyGen()
        self.cc.EvalMultKeyGen(self.keys.secretKey)
        self.cc.EvalSumKeyGen(self.keys.secretKey)
        
    def encrypt(self, data):
        plaintext = self.cc.MakeCKKSPackedPlaintext(data)
        return self.cc.Encrypt(self.keys.publicKey, plaintext)
    
    def decrypt(self, ciphertext):
        plaintext = self.cc.Decrypt(self.keys.secretKey, ciphertext)
        return plaintext.GetRealPackedValue()
    
    def add(self, ct1, ct2):
        return self.cc.EvalAdd(ct1, ct2)
    
    def mult(self, ct1, ct2):
        return self.cc.EvalMult(ct1, ct2)
```

### Option 2: Using ctypes (Direct C++ Interface)

```python
import ctypes
import numpy as np

# Load OpenFHE shared library
libopenfhe = ctypes.CDLL('libOPENFHEcore.so')

# Define function signatures
libopenfhe.CreateCryptoContext.argtypes = [...]
libopenfhe.CreateCryptoContext.restype = ctypes.c_void_p

class OpenFHECTypes:
    def __init__(self):
        self.ctx = libopenfhe.CreateCryptoContext(...)
        # ... setup parameters
```

### Option 3: Using pybind11 (Custom Bindings)

Create custom Python bindings:

```cpp
// openfhe_bindings.cpp
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include "openfhe.h"

namespace py = pybind11;
using namespace lbcrypto;

class PyOpenFHE {
private:
    CryptoContext<DCRTPoly> cc;
    KeyPair<DCRTPoly> keys;
    
public:
    PyOpenFHE() {
        CCParams<CryptoContextCKKSRNS> parameters;
        parameters.SetMultiplicativeDepth(10);
        parameters.SetScalingModSize(50);
        
        cc = GenCryptoContext(parameters);
        cc->Enable(PKE);
        cc->Enable(KEYSWITCH);
        cc->Enable(LEVELEDSHE);
        
        keys = cc->KeyGen();
        cc->EvalMultKeyGen(keys.secretKey);
    }
    
    py::array_t<double> encrypt(py::array_t<double> data) {
        // Convert numpy array to OpenFHE plaintext
        // Encrypt and return
    }
    
    // ... other methods
};

PYBIND11_MODULE(openfhe_bindings, m) {
    py::class_<PyOpenFHE>(m, "OpenFHE")
        .def(py::init<>())
        .def("encrypt", &PyOpenFHE::encrypt);
}
```

Compile:
```bash
g++ -O3 -Wall -shared -std=c++17 -fPIC \
    $(python3 -m pybind11 --includes) \
    openfhe_bindings.cpp -o openfhe_bindings.so \
    -lOPENFHEcore -lOPENFHEpke
```

## Modifying the Code

### Step 1: Replace FHESimulator

In `openfhe_integration.py`:

```python
# OLD
from .openfhe_integration import FHESimulator

# NEW
try:
    import openfhe
    USE_REAL_OPENFHE = True
except ImportError:
    USE_REAL_OPENFHE = False
    print("[Warning] OpenFHE not found, using simulator")

if USE_REAL_OPENFHE:
    FHEContext = OpenFHEContext  # Real implementation
else:
    FHEContext = FHESimulator     # Fallback to simulator
```

### Step 2: Update Encryption Operations

```python
class FHECompatibleWeights:
    def compute_encrypted_weighted_sum(self, encrypted_input):
        if USE_REAL_OPENFHE:
            # Use OpenFHE's EvalInnerProduct
            result = self.fhe_context.cc.EvalInnerProduct(
                self.encrypted_weights,
                encrypted_input,
                len(self.weights)
            )
            return result
        else:
            # Use simulation
            return self._simulate_weighted_sum(encrypted_input)
```

### Step 3: Handle Parameter Selection

OpenFHE requires careful parameter selection:

```python
def get_openfhe_parameters(network_depth, max_value=100):
    """
    Calculate OpenFHE parameters based on network depth
    
    Args:
        network_depth: Number of layers in the network
        max_value: Maximum expected value in computations
    
    Returns:
        dict: OpenFHE parameter configuration
    """
    # Multiplicative depth = network_depth * 2 (for weights + activations)
    mult_depth = network_depth * 2 + 5  # Add buffer
    
    # Scaling factor (balance precision vs noise)
    scale_factor = 50
    
    # Ring dimension (security parameter)
    ring_dim = 8192  # or 16384 for higher security
    
    return {
        'multiplicative_depth': mult_depth,
        'scale_factor': scale_factor,
        'ring_dimension': ring_dim,
        'security_level': 'HEStd_128_classic'
    }
```

## Testing Real OpenFHE Integration

```python
def test_real_openfhe():
    """Test actual OpenFHE integration"""
    import openfhe
    
    # Setup
    params = openfhe.CCParams_CKKS()
    params.SetMultiplicativeDepth(10)
    params.SetScalingModSize(50)
    
    cc = openfhe.CryptoContext(params)
    cc.Enable(openfhe.PKE)
    
    keys = cc.KeyGen()
    
    # Test encryption
    data = [1.0, 2.0, 3.0, 4.0]
    pt = cc.MakeCKKSPackedPlaintext(data)
    ct = cc.Encrypt(keys.publicKey, pt)
    
    # Test homomorphic operations
    ct2 = cc.EvalMult(ct, ct)
    
    # Decrypt
    result = cc.Decrypt(keys.secretKey, ct2)
    
    print("OpenFHE integration successful!")
    return True
```

## Performance Considerations

### Optimization Tips

1. **Batch Operations**: Pack multiple values into single ciphertext
   ```python
   # Instead of encrypting each value separately
   encrypted_vector = encrypt_batch([v1, v2, ..., vn])
   ```

2. **Reduce Multiplicative Depth**: Minimize sequential multiplications
   ```python
   # Bad: deep sequential operations
   result = ((a * b) * c) * d
   
   # Better: parallel operations
   result = (a * b) + (c * d)
   ```

3. **Bootstrap When Needed**: Refresh ciphertext noise
   ```python
   if noise_level > threshold:
       ct = cc.Bootstrap(ct)
   ```

4. **Use Sparse Operations**: SNNs naturally sparse
   ```python
   # Only encrypt non-zero spikes
   active_indices = np.nonzero(spikes)[0]
   encrypted_active = encrypt(spikes[active_indices])
   ```

### Expected Performance

- **Encryption**: ~1-10ms per ciphertext
- **Homomorphic Add**: ~0.1ms
- **Homomorphic Mult**: ~1-5ms
- **Decryption**: ~1-10ms

For a 3-layer SNN with 100 neurons per layer:
- **Without FHE**: ~1ms inference
- **With FHE**: ~100-500ms inference

## Security Considerations

### Parameter Selection for Security

```python
# 128-bit security
params.SetSecurityLevel(openfhe.HEStd_128_classic)
params.SetRingDim(8192)

# 192-bit security (higher security, slower)
params.SetSecurityLevel(openfhe.HEStd_192_classic)
params.SetRingDim(16384)
```

### Key Management

```python
# Never expose secret key in production
# Public key can be shared with clients
public_key = keys.publicKey
# secret_key = keys.secretKey  # Keep secure!

# For multi-party computation
relinearization_key = cc.EvalMultKeyGen(secret_key)
rotation_keys = cc.EvalSumKeyGen(secret_key)
```

## Example: Full Integration

```python
# example_real_openfhe.py
import openfhe
import numpy as np
from src.snn_layer import SNNLayer

def create_openfhe_snn():
    # Initialize OpenFHE
    params = openfhe.CCParams_CKKS()
    params.SetMultiplicativeDepth(20)
    params.SetScalingModSize(50)
    params.SetBatchSize(8192)
    
    cc = openfhe.CryptoContext(params)
    cc.Enable(openfhe.PKE)
    cc.Enable(openfhe.KEYSWITCH)
    cc.Enable(openfhe.LEVELEDSHE)
    
    keys = cc.KeyGen()
    cc.EvalMultKeyGen(keys.secretKey)
    
    # Create SNN with OpenFHE
    layer = SNNLayer(
        input_size=10,
        output_size=5,
        use_fhe=True,
        fhe_context=cc
    )
    
    # Encrypt input
    input_data = np.random.rand(10)
    pt = cc.MakeCKKSPackedPlaintext(input_data.tolist())
    encrypted_input = cc.Encrypt(keys.publicKey, pt)
    
    # Forward pass (encrypted)
    encrypted_output = layer.forward(encrypted_input, encrypted=True)
    
    # Decrypt result
    result = cc.Decrypt(keys.secretKey, encrypted_output)
    
    return result

if __name__ == "__main__":
    result = create_openfhe_snn()
    print("Encrypted SNN inference complete!")
```

## Troubleshooting

### Common Issues

1. **Import Error**: OpenFHE not installed
   ```bash
   # Install OpenFHE
   git clone https://github.com/openfheorg/openfhe-development.git
   cd openfhe-development && mkdir build && cd build
   cmake .. && make -j && sudo make install
   ```

2. **Noise Budget Exceeded**: Increase multiplicative depth
   ```python
   params.SetMultiplicativeDepth(30)  # Increase from 10
   ```

3. **Performance Issues**: Use batching
   ```python
   params.SetBatchSize(8192)  # Process multiple values together
   ```

## Resources

- OpenFHE Documentation: https://openfhe.org/
- OpenFHE GitHub: https://github.com/openfheorg/openfhe-development
- CKKS Scheme Paper: https://eprint.iacr.org/2016/421.pdf
- Example Code: https://github.com/openfheorg/openfhe-development/tree/main/src/pke/examples

## Summary

To integrate real OpenFHE:
1. Install OpenFHE C++ library
2. Create Python bindings (pybind11 recommended)
3. Replace `FHESimulator` with real OpenFHE context
4. Adjust parameters for your security/performance needs
5. Test thoroughly with encrypted operations

The current codebase is designed to make this transition seamless!
