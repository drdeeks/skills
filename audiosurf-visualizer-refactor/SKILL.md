---
name: audiosurf-visualizer-refactor
description: "Create immersive, enterprise-grade, audio-reactive 3D visualizers inspired by AudioSurf — neon-drenched racing tracks, beat-synced particle explosions, and procedural environments that dance to any audio source. Provider-agnostic: works with any LLM backend (OpenAI, Claude, Mistral, Gemini, Hermes, Copilot, or any agent with tool use). Free-first: 100% $0 open-source stack (Three.js, React Three Fiber, Web Audio API). Use when: building music visualizers, audio-reactive 3D experiences, beat-synced WebGL games, frequency-driven particle systems, neon racing games, or any project combining real-time audio analysis with 3D graphics."
version: 0.0.4
---

# AudioSurf Visualizer

Enterprise-grade skill for building audio-reactive 3D racing visualizers. Combines real-time 7-band spectral analysis, procedural neon track generation, adaptive performance scaling (5 quality tiers), and a vivid Bahamas-sunset-meets-frequency-waves color system — all on a 100% free open-source stack.

## Provider Compatibility

| Provider | Compatibility | Notes |
|---|---|---|
| MuleRun | Full | Native session, compute, drive support |
| Claude (Anthropic) | Full | MCP servers, tool use |
| OpenAI / ChatGPT | Full | Function calling, Actions |
| Mistral / Vibe | Full | Tool calling, script execution |
| Gemini (Google) | Full | Extensions, Vertex AI |
| Hermes (Nous) | Full | Tool-use fine-tuned |
| GitHub Copilot | Partial | Code generation only; use external runner for builds |
| Any LLM + tools | Full | Scripts are provider-independent Python |

## Free-First Strategy

| Tier | Cost | Stack |
|---|---|---|
| **Tier 0** | $0/mo | Three.js + R3F + Web Audio API + Meyda (all MIT) |
| **Tier 1** | $0-10/mo | + Vercel/Netlify hosting for deployment |
| **Tier 2** | $10-30/mo | + Custom domain + CDN for production |

Escalation: Never upgrade until Tier 0 is validated. The entire core stack is permanently free.

## Core Stack

| Component | Role | Cost | License |
|---|---|---|---|
| Three.js | 3D rendering engine | $0 | MIT |
| React Three Fiber | React renderer for Three.js | $0 | MIT |
| @react-three/postprocessing | Bloom, chromatic aberration, vignette | $0 | MIT |
| @react-three/drei | Helpers (shaderMaterial, Stars, etc.) | $0 | MIT |
| Web Audio API | Audio decoding, FFT analysis | $0 | Browser built-in |
| Meyda | Spectral feature extraction | $0 | MIT |
| Leva | Debug controls panel | $0 | MIT |

## Architecture — Three Layers

```
┌─────────────────────────────────────────────────┐
│  Layer 1: Audio Analysis Pipeline               │
│  Web Audio API → FFT → 7-Band Split → Features  │
│  Beat detection, spectral centroid, RMS energy   │
├─────────────────────────────────────────────────┤
│  Layer 2: Procedural 3D World (R3F)             │
│  Track (TubeGeometry + GLSL shaders)            │
│  Particles (instanced, beat-reactive)           │
│  Environment (stars, floating objects, fog)      │
│  Post-processing (bloom, chromatic aberration)  │
├─────────────────────────────────────────────────┤
│  Layer 3: Adaptive Performance Tuner            │
│  Hardware detection → 5 tiers (potato → ultra)  │
│  Real-time FPS monitoring → auto tier switching │
└─────────────────────────────────────────────────┘
```

## Workflow: Build a Visualizer

### Step 1: Scaffold Project

```bash
npm create vite@latest audiosurf -- --template react-ts
cd audiosurf
npm install three @react-three/fiber @react-three/drei @react-three/postprocessing postprocessing meyda leva
npm install -D @types/three vite-plugin-glsl
```

Configure `vite.config.ts` to import `.glsl` files:
```typescript
import glsl from 'vite-plugin-glsl';
export default defineConfig({ plugins: [react(), glsl()] });
```

### Step 2: Generate Core Modules

Run scripts to generate the audio pipeline and performance tuner:
```bash
python3 scripts/audio_pipeline.py generate --fft 2048
python3 scripts/performance_profiler.py generate --target-fps 60
```

These produce `src/audio/AudioAnalyzer.ts` and `src/systems/PerformanceTuner.ts`.

### Step 3: Build the Audio-Reactive Track

Read [references/shader-library.md](references/shader-library.md) for complete GLSL vertex + fragment shaders.

Key track construction pattern:
```typescript
const curve = new THREE.CatmullRomCurve3(controlPoints);
const geometry = new THREE.TubeGeometry(curve, 800, 2, 8, false);
// Apply custom ShaderMaterial with audio uniforms
// Update uniforms every frame from AudioAnalyzer.getFeatures()
```

Read [references/audio-analysis-guide.md](references/audio-analysis-guide.md) for the visual mapping matrix — which audio feature drives which visual parameter.

### Step 4: Add Reactive Environment

Build these elements around the track:
- **Starfield**: Instanced Points on a sphere, twinkle + beat flash
- **Floating objects**: Icosahedrons/tori with beat-phase scale pulsing
- **Light beams**: Spotlights mapped to frequency bands
- **Post-processing**: Bloom (essential), ChromaticAberration, Vignette

Read [references/visual-design-system.md](references/visual-design-system.md) for the complete color palette, glow pipeline, and post-processing stack configuration.

### Step 5: Integrate Performance Tuner

The tuner auto-detects hardware on init and dynamically adjusts quality every frame:
```typescript
const tuner = new PerformanceTuner();

useFrame(() => {
  const fps = 1 / delta;
  const changed = tuner.tick(fps);
  if (changed) {
    const profile = tuner.getProfile();
    // Apply profile.maxParticles, profile.bloomEnabled, etc.
  }
});
```

Read [references/performance-tuning.md](references/performance-tuning.md) for tier definitions, optimization techniques, and memory management.

### Step 6: Wire Audio Input

Support both file upload and microphone:
```typescript
// File: URL.createObjectURL(file) → <audio> element → AudioAnalyzer.init()
// Mic: navigator.mediaDevices.getUserMedia() → MediaStreamSource → AnalyserNode
```

### Step 7: Polish & Ship

- Add HTML overlay HUD (song title, BPM, frequency bars)
- Add Leva debug panel for manual tier override and color tweaking
- Test across browsers (Safari AudioContext quirks — see error-handling.md)

## Workflow: Quick Frequency Bar Visualizer (2D Fallback)

For simpler use cases or WebGL fallback:

1. Use `<canvas>` 2D context
2. Draw frequency bars from `getByteFrequencyData()`
3. Apply neon color palette with `ctx.shadowBlur` for glow
4. Sync bar heights to 7-band split

This serves as the graceful degradation path when WebGL is unavailable.

## Scripts

| Script | Purpose |
|---|---|
| `scripts/setup.py` | Environment validation, dependency check, state directory scaffolding |
| `scripts/audio_pipeline.py` | Generates the TypeScript audio analysis module with configurable FFT/bands |
| `scripts/performance_profiler.py` | Generates the adaptive performance tuner with 5 quality tiers |

## Enforced Output Statistics

Every build/generation operation concludes with:

```json
{
  "operation": "operation_name",
  "timestamp": "ISO8601",
  "status": "success | partial | failed",
  "duration_seconds": 0.0,
  "config": {},
  "output": "file_path",
  "cost": {"tier": 0, "amount_usd": 0.0, "service": "local"}
}
```

Statistics are appended to `~/.audiosurf-visualizer/analytics/run_stats.jsonl`. Output is non-negotiable — if data is unavailable, use `[pending]` markers.

## Error Handling

| Error Type | Response |
|---|---|
| AudioContext suspended | Prompt user gesture, resume on click |
| Audio decode failure | Show supported formats (.mp3, .wav, .ogg, .flac) |
| WebGL context lost | Pause render, attempt recovery, fallback to 2D |
| Shader compile error | Fallback to MeshStandardMaterial with emissive |
| FPS < 20 at potato tier | Degrade to 2D canvas visualizer |
| CORS audio block | Instruct on crossOrigin attribute + server headers |

See [references/error-handling.md](references/error-handling.md) for full error catalog, browser-specific workarounds, and graceful degradation stages.

## Enhancement Hooks

| Skill | Enhancement | When to Add |
|---|---|---|
| `html-report` | Visual performance analytics dashboard | When profiling across devices |
| `frontend-design` | Premium UI/UX for controls and overlays | When building production UI |
| `playwright-cli` | Automated cross-browser visual testing | When validating browser compat |
| `xlsx` | Export audio analysis data to spreadsheet | When doing audio research |
| `mulerouter-skills` | Generate album art or background textures | When adding AI-generated visuals |

## Key References

- **GLSL shaders for track, particles, and environment**: [references/shader-library.md](references/shader-library.md) — Read when implementing any 3D visual element
- **Audio analysis, FFT, beat detection, visual mapping matrix**: [references/audio-analysis-guide.md](references/audio-analysis-guide.md) — Read when connecting audio to visuals
- **Color palette, glow pipeline, post-processing, camera motion**: [references/visual-design-system.md](references/visual-design-system.md) — Read when designing the visual aesthetic
- **Adaptive quality tiers, hardware detection, optimization**: [references/performance-tuning.md](references/performance-tuning.md) — Read when tuning performance
- **Error catalog, browser quirks, graceful degradation**: [references/error-handling.md](references/error-handling.md) — Read when handling failures

## Sources

- **Three.js Documentation**: https://threejs.org/docs/
- **React Three Fiber**: https://r3f.docs.pmnd.rs/
- **Web Audio API**: https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API
- **Vercel Documentation**: https://vercel.com/docs
- **Netlify Documentation**: https://docs.netlify.com
