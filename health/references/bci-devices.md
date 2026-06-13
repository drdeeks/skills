# BCI Devices Reference

## Overview

Brain-Computer Interface (BCI) devices for health monitoring and neurofeedback applications.

## Consumer Devices

### Muse
- **Manufacturer**: InteraXon
- **Sensors**: EEG (4-7 channels)
- **Connection**: Bluetooth
- **SDK**: Python, JavaScript
- **Use Cases**: Meditation, sleep tracking, focus training

### OpenBCI
- **Manufacturer**: OpenBCI
- **Sensors**: EEG (8-16 channels)
- **Connection**: Bluetooth, USB
- **SDK**: Python, JavaScript
- **Use Cases**: Research, neurofeedback, custom applications

### Emotiv
- **Manufacturer**: Emotiv
- **Sensors**: EEG (5-14 channels)
- **Connection**: Bluetooth
- **SDK**: Python, C#
- **Use Cases**: Cognitive monitoring, mental state tracking

## Medical-Grade Devices

### NeuroPace
- **Type**: Responsive neurostimulation
- **FDA Approved**: Yes
- **Use Cases**: Epilepsy treatment

### BrainGate
- **Type**: Implanted BCI
- **Research Use**: Yes
- **Use Cases**: paralysis rehabilitation

## Data Formats

### EEG Data
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "channels": {
    "Fp1": 12.5,
    "Fp2": 11.8,
    "F3": 10.2,
    "F4": 11.1,
    "C3": 9.8,
    "C4": 10.5,
    "P3": 8.9,
    "P4": 9.2
  },
  "sampling_rate": 256,
  "impedances": {
    "Fp1": 5.2,
    "Fp2": 4.8
  }
}
```

### Signal Processing
```python
import numpy as np
from scipy import signal

def preprocess_eeg(raw_data, sampling_rate=256):
    """Preprocess EEG data."""
    # Bandpass filter (1-50 Hz)
    b, a = signal.butter(4, [1, 50], btype='band')
    filtered = signal.filtfilt(b, a, raw_data)
    
    # Notch filter (50/60 Hz)
    b, a = signal.iirnotch(50, 30, sampling_rate)
    filtered = signal.filtfilt(b, a, filtered)
    
    return filtered
```

## Integration Patterns

### Real-time Streaming
```python
import asyncio
from muse import Muse

async def stream_eeg():
    muse = Muse()
    await muse.connect()
    
    async for data in muse.stream():
        process_eeg_data(data)

asyncio.run(stream_eeg())
```

### Batch Processing
```python
import pandas as pd
from scipy import signal

def analyze_eeg_file(file_path):
    """Analyze EEG data from file."""
    data = pd.read_csv(file_path)
    
    # Apply filters
    filtered = preprocess_eeg(data.values)
    
    # Calculate features
    features = extract_features(filtered)
    
    return features
```

## Best Practices

1. **Calibrate devices** - Follow manufacturer calibration procedures
2. **Minimize noise** - Use proper electrode placement
3. **Validate data** - Check signal quality before analysis
4. **Respect privacy** - Handle biometric data securely
5. **Follow regulations** - Comply with health data laws (HIPAA, GDPR)