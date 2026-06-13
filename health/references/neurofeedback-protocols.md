# Neurofeedback Protocols Reference

## Overview

Neurofeedback training protocols for cognitive enhancement and health optimization.

## Common Protocols

### Alpha Training (8-12 Hz)
**Purpose**: Relaxation, stress reduction
**Application**: Anxiety, ADHD, peak performance

```python
def alpha_training(data, sampling_rate=256):
    """Extract and train alpha waves."""
    # Bandpass filter for alpha
    b, a = signal.butter(4, [8, 12], btype='band')
    alpha = signal.filtfilt(b, a, data)
    
    # Calculate power
    power = np.mean(alpha ** 2)
    
    # Feedback
    if power > threshold:
        return "positive_feedback"
    else:
        return "neutral_feedback"
```

### Beta Training (12-30 Hz)
**Purpose**: Focus, concentration, alertness
**Application**: ADHD, cognitive enhancement

```python
def beta_training(data, sampling_rate=256):
    """Extract and train beta waves."""
    # Bandpass filter for beta
    b, a = signal.butter(4, [12, 30], btype='band')
    beta = signal.filtfilt(b, a, data)
    
    # Calculate power
    power = np.mean(beta ** 2)
    
    return power
```

### Theta Training (4-8 Hz)
**Purpose**: Creativity, meditation, deep relaxation
**Application**: Anxiety, insomnia, creative enhancement

```python
def theta_training(data, sampling_rate=256):
    """Extract and train theta waves."""
    # Bandpass filter for theta
    b, a = signal.butter(4, [4, 8], btype='band')
    theta = signal.filtfilt(b, a, data)
    
    # Calculate power
    power = np.mean(theta ** 2)
    
    return power
```

### SMR Training (12-15 Hz)
**Purpose**: Calm focus, sensorimotor rhythm
**Application**: ADHD, epilepsy, sleep disorders

```python
def smr_training(data, sampling_rate=256):
    """Extract and train SMR waves."""
    # Bandpass filter for SMR
    b, a = signal.butter(4, [12, 15], btype='band')
    smr = signal.filtfilt(b, a, data)
    
    # Calculate power
    power = np.mean(smr ** 2)
    
    return power
```

## Advanced Protocols

### Z-Score Training
**Purpose**: Normalize brain activity to population norms
**Application**: Various neurological conditions

```python
def zscore_training(data, normative_data):
    """Apply Z-score training."""
    # Calculate Z-scores
    z_scores = {}
    for band in ['delta', 'theta', 'alpha', 'beta']:
        power = calculate_band_power(data, band)
        mean = np.mean(normative_data[band])
        std = np.std(normative_data[band])
        z_scores[band] = (power - mean) / std
    
    return z_scores
```

### Coherence Training
**Purpose**: Improve communication between brain regions
**Application**: Learning disabilities, cognitive enhancement

```python
def coherence_training(data1, data2):
    """Train coherence between two brain regions."""
    # Calculate coherence
    coherence = signal.coherence(data1, data2, fs=256)
    
    # Average coherence in frequency band
    avg_coherence = np.mean(coherence)
    
    return avg_coherence
```

## Feedback Modalities

### Visual Feedback
```python
def visual_feedback(power, threshold):
    """Provide visual feedback based on power."""
    if power > threshold:
        return {"color": "green", "animation": "success"}
    else:
        return {"color": "red", "animation": "neutral"}
```

### Audio Feedback
```python
def audio_feedback(power, threshold):
    """Provide audio feedback based on power."""
    if power > threshold:
        return {"sound": "chime", "volume": 0.5}
    else:
        return {"sound": "silence"}
```

### Haptic Feedback
```python
def haptic_feedback(power, threshold):
    """Provide haptic feedback based on power."""
    if power > threshold:
        return {"vibration": "pulse", "duration": 100}
    else:
        return {"vibration": "none"}
```

## Session Structure

### Typical Session
1. **Baseline** (2-5 minutes): Record resting state
2. **Training** (20-30 minutes): Active neurofeedback
3. **Review** (5-10 minutes): Analyze progress

### Frequency
- **Beginner**: 2-3 sessions per week
- **Intermediate**: 3-4 sessions per week
- **Advanced**: Daily sessions

## Best Practices

1. **Start simple** - Begin with basic protocols
2. **Track progress** - Log sessions and improvements
3. **Personalize** - Adjust protocols based on individual response
4. **Be patient** - Neurofeedback requires consistency
5. **Consult professionals** - Work with trained practitioners