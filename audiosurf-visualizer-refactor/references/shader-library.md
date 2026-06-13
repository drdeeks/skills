# AudioSurf Visualizer — GLSL Shader Library

Complete shader reference for audio-reactive track rendering, particle systems, environment effects, and post-processing.

## Table of Contents

1. [Track Surface Shader](#1-track-surface-shader)
2. [Particle System Shader](#2-particle-system-shader)
3. [Skybox & Environment Shader](#3-skybox--environment-shader)
4. [Integration Patterns](#4-integration-patterns)

---

## 1. Track Surface Shader

The track is the visual centerpiece. It uses a `TubeGeometry` extruded along a `CatmullRomCurve3` path with custom vertex displacement and neon grid fragment rendering.

### Vertex Shader — `trackVertex.glsl`

```glsl
varying vec3 vPosition;
varying vec3 vNormal;
varying vec2 vUv;
varying float vEnergy;

uniform float uTime;
uniform float uSubBass;
uniform float uBass;
uniform float uMid;
uniform float uTreble;
uniform float uBrilliance;
uniform float uEnergy;
uniform float uBeatPulse;
uniform float uBeatPhase;
uniform float uSpeed;

void main() {
  vUv = uv;
  vNormal = normalize(normalMatrix * normal);

  vec3 pos = position;

  // Sub-bass: deep slow-rolling displacement
  float waveSub = sin(pos.x * 1.2 + uTime * 0.8) * uSubBass * 0.2;

  // Bass: sharp rhythmic punch
  float waveBass = sin(pos.x * 3.0 + uTime * 2.5) * uBass * 0.15;
  waveBass += cos(pos.z * 2.0 + uTime * 1.8) * uBass * 0.08;

  // Mid: melodic undulation
  float waveMid = sin(pos.x * 5.0 + pos.z * 3.0 + uTime * 3.5) * uMid * 0.06;

  // Treble: fine high-frequency ripple
  float waveTreble = sin(pos.x * 12.0 + pos.z * 8.0 + uTime * 6.0) * uTreble * 0.025;

  // Beat pulse: uniform expansion on hits
  float pulse = 1.0 + uBeatPulse * 0.03;
  pos += normal * (waveSub + waveBass + waveMid + waveTreble);
  pos *= pulse;

  vPosition = (modelViewMatrix * vec4(pos, 1.0)).xyz;
  vEnergy = uEnergy;

  gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
}
```

### Fragment Shader — `trackFragment.glsl`

```glsl
varying vec3 vPosition;
varying vec3 vNormal;
varying vec2 vUv;
varying float vEnergy;

uniform float uTime;
uniform float uBass;
uniform float uMid;
uniform float uTreble;
uniform float uEnergy;
uniform float uBeatPulse;
uniform float uSpeed;
uniform float uSpectralCentroid;
uniform vec3 uColorA;  // primary neon (e.g., cyan #00f5ff)
uniform vec3 uColorB;  // secondary neon (e.g., magenta #ff00e4)
uniform vec3 uColorC;  // accent (e.g., electric yellow #f0ff00)

void main() {
  vec3 viewDir = normalize(-vPosition);
  float fresnel = pow(1.0 - max(dot(viewDir, vNormal), 0.0), 3.5);

  // Neon grid lines
  float gridX = smoothstep(0.94, 0.96, fract(vUv.x * 24.0));
  float gridY = smoothstep(0.94, 0.96, fract(vUv.y * 12.0 + uTime * uSpeed * 0.3));
  float grid = max(gridX, gridY);

  // Scrolling energy pattern
  float scroll = sin(vUv.x * 40.0 + uTime * 5.0) * 0.5 + 0.5;
  scroll *= sin(vUv.y * 20.0 - uTime * 3.0) * 0.5 + 0.5;
  scroll *= uEnergy * 0.2;

  // Color mixing driven by spectral centroid
  vec3 baseColor = mix(uColorA, uColorB, uSpectralCentroid);
  vec3 gridColor = mix(uColorB, uColorC, uBass);

  // Compose
  vec3 color = baseColor * 0.15;                          // ambient
  color += gridColor * grid * (0.6 + uBass * 0.4);       // neon grid
  color += uColorA * fresnel * (0.4 + uEnergy * 0.6);    // rim glow
  color += uColorC * scroll;                              // energy pattern

  // Beat flash
  color += vec3(1.0) * uBeatPulse * 0.15;

  // Edge glow (brighter at track edges)
  float edge = smoothstep(0.0, 0.25, vUv.x) * smoothstep(1.0, 0.75, vUv.x);
  color += uColorB * (1.0 - edge) * 0.4;

  // Emissive boost
  float emissive = 0.08 + uEnergy * 0.35 + uBeatPulse * 0.25;
  color += baseColor * emissive;

  gl_FragColor = vec4(color, 0.92);
}
```

### Uniform Update Pattern (R3F)

```tsx
useFrame((state) => {
  const { bands, beat, energy, spectralCentroid } = audioAnalyzer.getFeatures();
  if (trackMaterialRef.current) {
    const u = trackMaterialRef.current.uniforms;
    u.uTime.value = state.clock.elapsedTime;
    u.uSubBass.value = THREE.MathUtils.lerp(u.uSubBass.value, bands.sub, 0.15);
    u.uBass.value = THREE.MathUtils.lerp(u.uBass.value, bands.bass, 0.2);
    u.uMid.value = THREE.MathUtils.lerp(u.uMid.value, bands.mid, 0.12);
    u.uTreble.value = THREE.MathUtils.lerp(u.uTreble.value, bands.treble, 0.1);
    u.uBrilliance.value = THREE.MathUtils.lerp(u.uBrilliance.value, bands.brilliance, 0.08);
    u.uEnergy.value = THREE.MathUtils.lerp(u.uEnergy.value, energy, 0.15);
    u.uBeatPulse.value = beat.beatIntensity;
    u.uSpectralCentroid.value = spectralCentroid;
  }
});
```

---

## 2. Particle System Shader

Beat-reactive particle explosions and ambient particle fields.

### Vertex Shader — `particleVertex.glsl`

```glsl
attribute float aSize;
attribute float aLife;
attribute vec3 aVelocity;
attribute float aPhase;

varying float vLife;
varying float vPhase;

uniform float uTime;
uniform float uBeatPulse;
uniform float uEnergy;

void main() {
  vLife = aLife;
  vPhase = aPhase;

  vec3 pos = position + aVelocity * uTime;

  // Beat burst: expand outward on hits
  pos += aVelocity * uBeatPulse * 2.0;

  // Gravity-like drift
  pos.y -= uTime * uTime * 0.5 * (1.0 - uEnergy);

  vec4 mvPos = modelViewMatrix * vec4(pos, 1.0);
  gl_Position = projectionMatrix * mvPos;

  // Size attenuation + beat pulse
  float size = aSize * (1.0 + uBeatPulse * 0.5);
  gl_PointSize = size * (300.0 / -mvPos.z);
}
```

### Fragment Shader — `particleFragment.glsl`

```glsl
varying float vLife;
varying float vPhase;

uniform vec3 uParticleColorA;
uniform vec3 uParticleColorB;
uniform float uTime;

void main() {
  // Soft circle
  float dist = length(gl_PointCoord - vec2(0.5));
  if (dist > 0.5) discard;

  float alpha = smoothstep(0.5, 0.1, dist) * vLife;

  // Color shift over lifetime
  vec3 color = mix(uParticleColorA, uParticleColorB, vPhase);

  // Hot center
  color += vec3(0.5) * smoothstep(0.2, 0.0, dist);

  gl_FragColor = vec4(color, alpha);
}
```

---

## 3. Skybox & Environment Shader

Procedural deep-space background with nebula and reactive star field.

### Fragment Shader — `envFragment.glsl`

```glsl
varying vec3 vWorldPosition;

uniform float uTime;
uniform float uEnergy;
uniform float uBass;
uniform vec3 uNebulaColor1;  // deep purple #1a0033
uniform vec3 uNebulaColor2;  // dark teal #001a1a

// Simplex noise (include your preferred noise function)
float noise3d(vec3 p) {
  // ... standard 3D simplex noise implementation
  return 0.0; // placeholder
}

void main() {
  vec3 dir = normalize(vWorldPosition);

  // Base void color
  vec3 color = vec3(0.02, 0.02, 0.05);

  // Nebula clouds
  float n1 = noise3d(dir * 3.0 + uTime * 0.02) * 0.5 + 0.5;
  float n2 = noise3d(dir * 6.0 - uTime * 0.03) * 0.5 + 0.5;
  color += uNebulaColor1 * n1 * 0.15 * (0.5 + uBass * 0.5);
  color += uNebulaColor2 * n2 * 0.1;

  // Reactive energy wash
  float wash = noise3d(dir * 2.0 + uTime * 0.1) * uEnergy * 0.08;
  color += vec3(0.1, 0.0, 0.2) * wash;

  gl_FragColor = vec4(color, 1.0);
}
```

---

## 4. Integration Patterns

### ShaderMaterial Setup (R3F)

```tsx
import { shaderMaterial } from '@react-three/drei';
import trackVertex from '../shaders/trackVertex.glsl';
import trackFragment from '../shaders/trackFragment.glsl';

const TrackMaterial = shaderMaterial(
  {
    uTime: 0,
    uSubBass: 0,
    uBass: 0,
    uMid: 0,
    uTreble: 0,
    uBrilliance: 0,
    uEnergy: 0,
    uBeatPulse: 0,
    uBeatPhase: 0,
    uSpeed: 1.0,
    uSpectralCentroid: 0.5,
    uColorA: new THREE.Color('#00f5ff'),
    uColorB: new THREE.Color('#ff00e4'),
    uColorC: new THREE.Color('#f0ff00'),
  },
  trackVertex,
  trackFragment,
);

extend({ TrackMaterial });
```

### Color Palette Quick-Reference

| Name | Hex | Usage |
|---|---|---|
| Neon Cyan | `#00f5ff` | Primary track glow, rim light |
| Hot Magenta | `#ff00e4` | Grid lines, beat flash accent |
| Electric Yellow | `#f0ff00` | Energy scroll pattern, particle hot center |
| Laser Green | `#39ff14` | Alternative accent, spectral centroid mapping |
| Deep Violet | `#7b00ff` | Nebula, low-energy ambient |
| Sunset Orange | `#ff6b00` | High-energy override, BPM > 150 accent |
| Bahamas Coral | `#ff4d6a` | Warmth accent, low-mid band mapping |
| Void Black | `#0a0a14` | Background base |
| Deep Purple Nebula | `#1a0033` | Skybox cloud layer 1 |
| Dark Teal Nebula | `#001a1a` | Skybox cloud layer 2 |
