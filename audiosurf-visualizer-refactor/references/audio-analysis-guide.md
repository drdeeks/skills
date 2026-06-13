# AudioSurf Visualizer — Audio Analysis Guide

Deep reference for the Web Audio API integration, frequency band mapping, beat detection algorithms, and spectral feature extraction.

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Frequency Band Mapping](#2-frequency-band-mapping)
3. [Beat Detection](#3-beat-detection)
4. [Spectral Features](#4-spectral-features)
5. [Visual Mapping Matrix](#5-visual-mapping-matrix)
6. [Audio Source Handling](#6-audio-source-handling)

---

## 1. Architecture Overview

```
Audio Source (file / mic / stream)
    │
    ▼
AudioContext
    │
    ├──► MediaElementSource / MediaStreamSource
    │         │
    │         ▼
    │    AnalyserNode (FFT)
    │         │
    │         ├──► getByteFrequencyData()  → frequency spectrum
    │         └──► getFloatTimeDomainData() → waveform
    │
    └──► destination (speakers)

Post-FFT Pipeline:
    FrequencyData ──► Band Splitter (7 bands) ──► Smoothed bands
    FrequencyData ──► Spectral Features (centroid, flatness)
    TimeDomainData ──► RMS Energy
    Energy History ──► Beat Detector (threshold + BPM)
```

## 2. Frequency Band Mapping

7-band split optimized for visual mapping to distinct visual elements:

| Band | Range | Visual Target | Smoothing |
|---|---|---|---|
| **Sub** | 20-60 Hz | Track displacement (deep rolling waves) | 0.20 (slow) |
| **Bass** | 60-250 Hz | Beat pulse, camera shake, grid flash | 0.18 (responsive) |
| **Low-Mid** | 250-500 Hz | Ambient glow warmth, fog density | 0.15 |
| **Mid** | 500-2000 Hz | Floating object scale/rotation | 0.12 |
| **High-Mid** | 2-4 kHz | Light beam intensity, spotlight color | 0.10 |
| **Treble** | 4-8 kHz | Particle spawn rate, sparkle intensity | 0.08 (fast) |
| **Brilliance** | 8-20 kHz | Chromatic aberration, shimmer overlay | 0.06 (fastest) |

### Band Energy Calculation

```typescript
function getBandEnergy(freqData: Uint8Array, sampleRate: number, lowHz: number, highHz: number): number {
  const nyquist = sampleRate / 2;
  const binCount = freqData.length;
  const lowBin = Math.round((lowHz / nyquist) * binCount);
  const highBin = Math.round((highHz / nyquist) * binCount);
  let sum = 0;
  for (let i = lowBin; i < highBin && i < binCount; i++) {
    sum += freqData[i] / 255;
  }
  return sum / Math.max(1, highBin - lowBin);
}
```

### Smoothing (Exponential Moving Average)

Always smooth band values before mapping to visuals to avoid jitter:

```typescript
smoothedValue = THREE.MathUtils.lerp(smoothedValue, rawValue, smoothingFactor);
```

Lower smoothing factors = slower response = smoother motion. Match to the visual element's natural movement speed.

## 3. Beat Detection

Energy-threshold algorithm with adaptive sensitivity:

```
1. Compute current frame energy (RMS of time-domain signal)
2. Maintain rolling energy history (last 60 frames)
3. Calculate average energy over history
4. Beat = energy > (avgEnergy * threshold) AND (timeSinceLast > minInterval)
5. Log beat timestamp for BPM calculation
```

### Parameters

| Parameter | Default | Description |
|---|---|---|
| `threshold` | 1.4 | Beat = energy > avg * threshold |
| `minInterval` | 200ms | Minimum time between beats (prevents double-trigger) |
| `historySize` | 60 frames | Rolling energy window |
| `bpmRange` | 60-200 | Clamp BPM to musically valid range |

### BPM Estimation

From last 16 inter-beat intervals:

```typescript
const intervals = beatTimestamps.slice(-16).map((t, i, a) => i > 0 ? t - a[i-1] : 0).slice(1);
const avgInterval = intervals.reduce((a, b) => a + b) / intervals.length;
const bpm = Math.round(60000 / avgInterval);
```

### Beat Phase

Position within the current beat cycle (0-1), useful for smooth pulsing animations:

```typescript
const phase = ((now - lastBeatTime) % (60000 / bpm)) / (60000 / bpm);
```

## 4. Spectral Features

### Spectral Centroid

"Center of mass" of the frequency spectrum. High = bright/sharp sound, low = dark/warm.

Maps to: color temperature shifts, hue rotation.

```typescript
const centroid = weightedSum / totalMagnitude / binCount; // normalized 0-1
```

### Spectral Flatness

Ratio of geometric to arithmetic mean of spectrum. High = noise-like, low = tonal.

Maps to: particle randomness, shimmer intensity.

### RMS Energy

Root-mean-square of time-domain signal. Overall loudness proxy.

Maps to: bloom intensity, emissive strength, global brightness.

## 5. Visual Mapping Matrix

Master mapping table for connecting audio features to visual parameters:

| Audio Feature | Visual Parameter | Mapping | Range |
|---|---|---|---|
| `bands.sub` | Track vertex displacement (slow roll) | Linear | 0-0.2 units |
| `bands.bass` | Camera shake amplitude | Quadratic | 0-0.05 |
| `bands.bass` | Grid line brightness | Linear | 0.3-1.0 |
| `beat.beatIntensity` | Bloom intensity spike | Exponential decay | 0.5-2.0 |
| `beat.beatIntensity` | Chromatic aberration offset | Linear | 0-0.008 |
| `beat.isBeat` | Particle burst (spawn N particles) | On/off trigger | 0 or 50-200 |
| `beat.phase` | Floating object scale pulse | Sine wave | 0.8-1.2 |
| `bands.mid` | Floating object rotation speed | Linear | 0.5-3.0 rad/s |
| `bands.highMid` | Spotlight intensity | Linear | 0.2-1.0 |
| `bands.treble` | Particle spawn rate | Linear | 0-maxParticles/s |
| `bands.brilliance` | Chromatic aberration base | Linear | 0-0.003 |
| `energy` | Post-processing bloom base | Linear | 0.1-1.0 |
| `energy` | Track emissive intensity | Linear | 0.08-0.45 |
| `spectralCentroid` | Color A/B mix ratio | Linear | 0-1 |
| `spectralFlatness` | Particle velocity randomness | Linear | 0.5-2.0 |

## 6. Audio Source Handling

### File Upload

```typescript
const handleFile = (file: File) => {
  const url = URL.createObjectURL(file);
  audioElement.src = url;
  audioElement.load();
  audioElement.addEventListener('canplaythrough', () => {
    audioAnalyzer.init(audioElement);
  }, { once: true });
};
```

### Microphone Input

```typescript
const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
const source = audioContext.createMediaStreamSource(stream);
source.connect(analyser);
// Do NOT connect to destination (feedback loop)
```

### Cross-Origin Audio

For streaming URLs, set `crossOrigin = "anonymous"` on the audio element and ensure the server sends CORS headers. Without this, `createMediaElementSource` will throw a SecurityError.
