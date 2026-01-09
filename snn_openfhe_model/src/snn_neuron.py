"""
Spiking Neural Network Neuron Implementation
Implements Leaky Integrate-and-Fire (LIF) neuron model
"""

import numpy as np
from typing import List, Tuple


class LIFNeuron:
    """
    Leaky Integrate-and-Fire (LIF) Neuron Model
    
    This neuron model accumulates input current and fires a spike when
    the membrane potential exceeds a threshold. After firing, the potential
    resets and enters a refractory period.
    
    Attributes:
        threshold: Voltage threshold for spike generation
        reset_potential: Voltage after spike
        leak_factor: Leakage rate (0 to 1)
        refractory_period: Time steps where neuron cannot fire after spike
        dt: Time step size
    """
    
    def __init__(
        self,
        threshold: float = 1.0,
        reset_potential: float = 0.0,
        leak_factor: float = 0.9,
        refractory_period: int = 2,
        dt: float = 0.001
    ):
        self.threshold = threshold
        self.reset_potential = reset_potential
        self.leak_factor = leak_factor
        self.refractory_period = refractory_period
        self.dt = dt
        
        # State variables
        self.membrane_potential = reset_potential
        self.refractory_counter = 0
        self.spike_train = []
        
    def step(self, input_current: float) -> bool:
        """
        Advance neuron by one time step
        
        Args:
            input_current: Input current to the neuron
            
        Returns:
            bool: True if neuron fires a spike, False otherwise
        """
        spike = False
        
        # Check if in refractory period
        if self.refractory_counter > 0:
            self.refractory_counter -= 1
            return spike
        
        # Update membrane potential with leak and input
        self.membrane_potential = (
            self.membrane_potential * self.leak_factor + 
            input_current * self.dt
        )
        
        # Check for spike
        if self.membrane_potential >= self.threshold:
            spike = True
            self.membrane_potential = self.reset_potential
            self.refractory_counter = self.refractory_period
            self.spike_train.append(1)
        else:
            self.spike_train.append(0)
            
        return spike
    
    def reset(self):
        """Reset neuron state"""
        self.membrane_potential = self.reset_potential
        self.refractory_counter = 0
        self.spike_train = []


class VectorizedLIFNeurons:
    """
    Vectorized implementation of multiple LIF neurons for software acceleration
    
    Uses NumPy's vectorized operations for SIMD-like performance improvements
    without explicit low-level SIMD programming.
    """
    
    def __init__(
        self,
        n_neurons: int,
        threshold: float = 1.0,
        reset_potential: float = 0.0,
        leak_factor: float = 0.9,
        refractory_period: int = 2,
        dt: float = 0.001
    ):
        self.n_neurons = n_neurons
        self.threshold = threshold
        self.reset_potential = reset_potential
        self.leak_factor = leak_factor
        self.refractory_period = refractory_period
        self.dt = dt
        
        # Vectorized state variables
        self.membrane_potentials = np.full(n_neurons, reset_potential)
        self.refractory_counters = np.zeros(n_neurons, dtype=int)
        self.spike_trains = []
        
    def step(self, input_currents: np.ndarray) -> np.ndarray:
        """
        Vectorized time step for all neurons
        
        Args:
            input_currents: Array of input currents for each neuron
            
        Returns:
            np.ndarray: Boolean array indicating which neurons fired
        """
        # Create mask for neurons not in refractory period
        active_mask = self.refractory_counters == 0
        
        # Update membrane potentials (vectorized operation)
        self.membrane_potentials[active_mask] = (
            self.membrane_potentials[active_mask] * self.leak_factor +
            input_currents[active_mask] * self.dt
        )
        
        # Detect spikes (vectorized comparison)
        spikes = self.membrane_potentials >= self.threshold
        
        # Reset spiking neurons
        self.membrane_potentials[spikes] = self.reset_potential
        self.refractory_counters[spikes] = self.refractory_period
        
        # Decrease refractory counters
        self.refractory_counters = np.maximum(0, self.refractory_counters - 1)
        
        # Record spike train
        self.spike_trains.append(spikes.astype(int))
        
        return spikes
    
    def reset(self):
        """Reset all neurons"""
        self.membrane_potentials.fill(self.reset_potential)
        self.refractory_counters.fill(0)
        self.spike_trains = []
