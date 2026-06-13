# AudioSurf Visualizer — Performance Tuning Guide

Adaptive quality scaling, hardware detection, FPS targeting, and optimization techniques for smooth 60fps across all devices.

## Table of Contents

1. [Adaptive Quality System](#1-adaptive-quality-system)
2. [Hardware Detection](#2-hardware-detection)
3. [Optimization Techniques](#3-optimization-techniques)
4. [Memory Management](#4-memory-management)
5. [Profiling & Diagnostics](#5-profiling--diagnostics)

---

## 1. Adaptive Quality System

### Tier Definitions

| Tier | Target Devices | Key Characteristics |
|---|---|---|
| **Potato** | Integrated GPU, old mobile | No post-processing, minimal particles, 0.75x resolution |
| **Low** | Entry GPU, modern mobile | Bloom only, 150 particles, 1x resolution |
| **Medium** | Mid-range GPU | Full bloom + chromatic aberration, 400 particles, 1.5x DPR |
| **High** | Dedicated GPU (GTX/RX) | All effects, shadows, 800 particles, 2x DPR |
| **Ultra** | High-end (RTX/RX 6000+) | Maximum everything, volumetric light, 1500 particles |

### Scaling Algorithm

```
Every frame:
  1. Record current FPS
  2. Maintain 90-frame rolling average
  3. After 30-frame warmup:
     - If avgFPS < (targetFPS - 8): downgrade one tier, cooldown 120 frames
     - If avgFPS >= (targetFPS - 2): upgrade one tier, cooldown 120 frames
  4. Reset history after tier change
```

The 120-frame cooldown prevents oscillation between tiers. The asymmetric thresholds (downgrade at -8, upgrade at -2) create hysteresis — the system is quicker to drop quality than raise it, preventing frame drops.

### What Each Tier Controls

| Parameter | Potato | Low | Medium | High | Ultra |
|---|---|---|---|---|---|
| Pixel ratio | 0.75 | 1.0 | 1.5 | 2.0 | native |
| Max particles | 50 | 150 | 400 | 800 | 1500 |
| Track segments | 100 | 300 | 800 | 2000 | 4000 |
| Bloom | off | on | on | on | on |
| Chrom. aberration | off | off | on | on | on |
| Shadows | off | off | off | on | on |
| Motion blur | off | off | off | on | on |
| Volumetric light | off | off | off | on | on |
| Stars | 200 | 600 | 2000 | 4000 | 8000 |
| Floating objects | 3 | 6 | 12 | 20 | 35 |
| Trail length | 10 | 20 | 40 | 60 | 100 |

## 2. Hardware Detection

### WebGL Capability Probing

```typescript
const canvas = document.createElement('canvas');
const gl = canvas.getContext('webgl2') || canvas.getContext('webgl');
const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
const gpu = debugInfo ? gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL) : '';
const maxTextureSize = gl.getParameter(gl.MAX_TEXTURE_SIZE);
```

### GPU Classification Heuristics

| Signal | Detection | Tier |
|---|---|---|
| No WebGL | `getContext` returns null | Potato |
| Mobile UA + WebGL | `navigator.userAgent` check | Low |
| maxTexture < 4096 | Low-end integrated | Low |
| maxTexture >= 4096, no discrete GPU keyword | Mid-range | Medium |
| GPU contains `GTX`, `RX 5xx`, `RX 6xx` | Dedicated | High |
| GPU contains `RTX 30xx/40xx`, `RX 7xxx` | High-end | Ultra |

### Override

Always provide manual tier selection via UI (Leva controls or settings panel) — hardware detection is heuristic, not definitive.

## 3. Optimization Techniques

### Instanced Rendering

For stars, particles, and floating objects — use `InstancedMesh` instead of individual meshes:

```typescript
const mesh = new THREE.InstancedMesh(geometry, material, count);
// Set per-instance transform via mesh.setMatrixAt(index, matrix)
// Set per-instance color via mesh.setColorAt(index, color)
mesh.instanceMatrix.needsUpdate = true;
```

### Object Pooling

Pre-allocate particle arrays. Never create/destroy Three.js objects during the animation loop:

```typescript
// GOOD: Reset existing particle
particles[i].position.set(x, y, z);
particles[i].life = 1.0;

// BAD: Create new particle every frame
const p = new THREE.Mesh(geo, mat);  // ← GC pressure
```

### Geometry Budget

| Element | Vertex Budget | Technique |
|---|---|---|
| Track | 10K-50K | TubeGeometry, LOD by distance |
| Floating objects | 500 each | Low-poly icosahedrons (detail=1) |
| Particles | 4 verts each | Points (billboard quads) |
| Stars | 1 vert each | Points |
| Skybox | 6 quads | CubeTexture or shader sphere |

### Shader Optimizations

- Use `smoothstep` over `pow` where possible (cheaper)
- Avoid branching (`if/else`) in fragment shaders — use `step`/`mix`
- Pre-compute uniform values on CPU, not in shader
- Use `lowp`/`mediump` precision where full precision isn't needed

## 4. Memory Management

### Disposal Checklist

When unmounting or switching scenes, dispose of:

```typescript
geometry.dispose();
material.dispose();
texture.dispose();
renderTarget.dispose();
```

### Audio Context Cleanup

```typescript
audioAnalyzer.dispose();  // disconnects nodes, closes context
```

### Frame Budget

Target 16.67ms per frame at 60fps:
- Audio analysis: < 1ms
- Scene update (uniforms, positions): < 2ms
- Three.js render: < 10ms
- Post-processing: < 3ms
- Headroom: ~1ms

## 5. Profiling & Diagnostics

### Built-in Stats

```tsx
import { Stats } from '@react-three/drei';
// Add <Stats /> to the Canvas for FPS/MS/MB overlay
```

### Performance Logging

The `PerformanceTuner` logs tier changes. Enable verbose logging for diagnostics:

```typescript
console.log(`[PerfTuner] Tier: ${tuner.getTier()}, Avg FPS: ${tuner.getAvgFps().toFixed(1)}`);
```

### Common Bottlenecks

| Symptom | Likely Cause | Fix |
|---|---|---|
| Low FPS, GPU-bound | Too many draw calls | Use instancing, merge geometries |
| Low FPS, CPU-bound | Too many JS objects | Object pooling, reduce scene graph depth |
| Stuttering | GC pauses | Avoid allocations in render loop |
| Bloom artifacts | Threshold too low | Raise luminanceThreshold |
| Audio lag | Large FFT size | Reduce fftSize to 1024 |
