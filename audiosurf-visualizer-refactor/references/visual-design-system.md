# AudioSurf Visualizer — Visual Design System

The definitive aesthetic standard for achieving the "designer meets audio frequency waves, partying on a .wav, dancing into a vivid neon Bahamas sunset" look.

## Table of Contents

1. [Color System](#1-color-system)
2. [Neon Glow Pipeline](#2-neon-glow-pipeline)
3. [Track Design](#3-track-design)
4. [Reactive Environment](#4-reactive-environment)
5. [Post-Processing Stack](#5-post-processing-stack)
6. [Camera & Motion](#6-camera--motion)
7. [Typography & UI Overlay](#7-typography--ui-overlay)

---

## 1. Color System

### Primary Palette — "Bahamas Neon Sunset"

```
VOID:     #0a0a14  — Deep void background (near-black with blue tint)
CYAN:     #00f5ff  — Primary neon (track glow, rim light, high energy)
MAGENTA:  #ff00e4  — Secondary neon (grid lines, beat flash)
YELLOW:   #f0ff00  — Electric accent (energy pulses, particle centers)
GREEN:    #39ff14  — Laser highlight (spectral centroid > 0.6)
VIOLET:   #7b00ff  — Deep accent (low energy, ambient wash)
CORAL:    #ff4d6a  — Bahamas warmth (low-mid band, sunset transition)
ORANGE:   #ff6b00  — High-energy override (BPM > 150)
PINK:     #ff1493  — Deep pink pulse (sub-bass resonance)
TEAL:     #00ffc8  — Cool accent (spectral flatness > 0.4)
```

### Dynamic Color Rules

| Condition | Primary | Secondary | Accent |
|---|---|---|---|
| Default (energy < 0.3) | Cyan | Violet | — |
| Medium energy (0.3-0.6) | Cyan | Magenta | Yellow |
| High energy (0.6-0.8) | Magenta | Yellow | Orange |
| Peak energy (> 0.8) | Yellow | Orange | White flash |
| Low BPM (< 90) | Violet | Teal | Coral |
| High BPM (> 150) | Orange | Magenta | Yellow |
| Breakdown / quiet | Violet | Deep Teal | — |

### Color Lerping

Never snap between colors. Always use temporal interpolation:

```typescript
const lerpSpeed = 0.04; // slow, dreamy transitions
currentColor.lerp(targetColor, lerpSpeed);
```

For beat hits, use faster lerp (0.3) then decay back slowly (0.04).

## 2. Neon Glow Pipeline

The glow effect is the single most important visual element. Without proper bloom, the visualizer looks flat.

### Three-Layer Glow

1. **Emissive materials** — Objects emit their own light via `emissiveIntensity` driven by audio energy
2. **Bloom post-processing** — `UnrealBloomPass` or R3F `<Bloom>` catches emissive surfaces
3. **Fresnel rim glow** — Shader-based edge glow that intensifies with viewing angle

### Bloom Settings by Quality Tier

| Setting | Low | Medium | High | Ultra |
|---|---|---|---|---|
| Intensity | 0.4 | 0.7 | 1.0 | 1.3 |
| Radius | 0.3 | 0.5 | 0.8 | 1.0 |
| Threshold | 0.6 | 0.3 | 0.1 | 0.05 |
| Luminance Smoothing | 0.9 | 0.8 | 0.7 | 0.6 |

### Emissive Intensity Formula

```
emissive = baseEmissive + (energy * energyMultiplier) + (beatIntensity * beatMultiplier)

Where:
  baseEmissive = 0.08
  energyMultiplier = 0.35
  beatMultiplier = 0.25
```

## 3. Track Design

### Geometry

- **Path**: `CatmullRomCurve3` with 200+ control points
- **Surface**: `TubeGeometry` with radialSegments=8, tubularSegments=800+
- **Width**: Track appears as a wide ribbon (flatten tube vertically)

### Track Generation Rules

1. Path curves left/right mapped to spectral centroid shifts
2. Path slopes up/down mapped to energy changes
3. Track width pulses with bass energy
4. Speed illusion: scroll UV coordinates along V-axis at `uSpeed * elapsedTime`

### Obstacle/Block Placement

- Blocks spawn at beat timestamps
- Block height = beat intensity * maxHeight
- Block color = current accent color
- Block width spans 1-3 of 5 track lanes
- Blocks approach the camera (or camera approaches blocks)

### Track Material Properties

```typescript
{
  transparent: true,
  opacity: 0.92,
  side: THREE.DoubleSide,
  depthWrite: true,
  blending: THREE.AdditiveBlending, // for neon glow
}
```

## 4. Reactive Environment

### Starfield

- Instanced `Points` geometry with random positions on a large sphere
- Star count scales with performance tier (200-8000)
- Stars twinkle: `opacity = 0.5 + sin(time * twinkleSpeed + phase) * 0.5`
- On beat: brief star brightness flash

### Floating Objects

- Geometric primitives: `IcosahedronGeometry`, `TorusGeometry`, `OctahedronGeometry`
- Positioned around the track at varying distances
- Scale pulsing synced to `beat.phase`: `scale = 1.0 + sin(phase * PI * 2) * 0.2`
- Rotation speed driven by `bands.mid`
- Emissive color driven by `bands.highMid`

### Light Beams

- 3-5 vertical `SpotLight` or volumetric light cones
- Each mapped to a different frequency band
- Intensity: `0.2 + bandEnergy * 0.8`
- Color: band-specific from palette
- Slowly rotate around the track

### Fog / Atmosphere

- `THREE.FogExp2` with density driven by energy
- Low energy: denser fog (mysterious)
- High energy: fog clears (clarity, intensity)
- Fog color shifts with palette transitions

## 5. Post-Processing Stack

Using `@react-three/postprocessing` (wraps `postprocessing` library):

```tsx
<EffectComposer>
  <Bloom
    intensity={0.7 + energy * 0.6}
    luminanceThreshold={0.2}
    luminanceSmoothing={0.8}
    radius={0.8}
  />
  <ChromaticAberration
    offset={new THREE.Vector2(
      brilliance * 0.003 + beatIntensity * 0.006,
      brilliance * 0.002 + beatIntensity * 0.004
    )}
  />
  <Vignette darkness={0.5 + (1 - energy) * 0.3} />
  <Noise opacity={0.03} />  {/* subtle film grain */}
  <ToneMapping mode={ToneMappingMode.ACES_FILMIC} />
</EffectComposer>
```

### Effect Priority (disable in order for performance)

1. Keep: Bloom (essential for neon look)
2. Keep: ToneMapping (color accuracy)
3. Drop first: Noise (cosmetic)
4. Drop second: ChromaticAberration (flashy but expensive)
5. Drop third: Vignette (subtle)

## 6. Camera & Motion

### Default Camera

- Position: behind and slightly above the track, looking forward
- FOV: 75 (wide enough for immersion, narrow enough for focus)
- Near/Far: 0.1 / 1000

### Camera Shake

On bass hits, apply short camera shake:

```typescript
if (beat.isBeat) {
  const shakeIntensity = beat.beatIntensity * 0.04;
  camera.position.x += (Math.random() - 0.5) * shakeIntensity;
  camera.position.y += (Math.random() - 0.5) * shakeIntensity;
  // Decay over 100ms via lerp back to rest position
}
```

### Speed Feel

- Track scroll speed: base 1.0, increases subtly with BPM
- FOV pulse: widen slightly on beat (75 -> 78), snap back
- Forward motion: camera or track mesh moves along the curve path

## 7. Typography & UI Overlay

### HUD Elements (HTML overlay, not 3D)

- Song title + artist (top left, `font-family: monospace`, neon glow text-shadow)
- BPM counter (top right, pulsing opacity with beat)
- Frequency visualizer bar (bottom, thin horizontal bars per band)
- Performance tier indicator (bottom right, only in debug mode)

### Text Glow CSS

```css
.neon-text {
  font-family: 'JetBrains Mono', monospace;
  color: #00f5ff;
  text-shadow:
    0 0 4px #00f5ff,
    0 0 8px #00f5ff,
    0 0 16px #00f5ff44,
    0 0 32px #00f5ff22;
}
```
