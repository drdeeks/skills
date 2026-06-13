# AudioSurf Visualizer — Error Handling

Error catalog and recovery procedures for all failure modes.

## Table of Contents

1. [Error Categories](#error-categories)
2. [Recovery Procedures](#recovery-procedures)
3. [Error Logging](#error-logging)
4. [Graceful Degradation](#graceful-degradation)

---

## Error Categories

| Category | Examples | Response |
|---|---|---|
| **Audio Context** | `AudioContext` blocked by browser policy, suspended state | Prompt user interaction (click/tap), resume context |
| **Audio Source** | File decode error, unsupported format, CORS block | Show format error, suggest supported formats (.mp3, .wav, .ogg, .flac) |
| **WebGL** | Context lost, shader compilation error, no WebGL support | Fallback to 2D canvas visualizer, log GPU info |
| **Performance** | FPS drops below 20 despite potato tier | Reduce to minimal mode: 2D waveform only, disable 3D |
| **Memory** | Out of GPU memory, buffer allocation failure | Dispose unused resources, reduce texture sizes, warn user |
| **File I/O** | File too large (>500MB), corrupted file | Validate file size/type before processing, clear error message |
| **Browser** | Safari AudioContext quirks, Firefox shader differences | Browser-specific workarounds documented below |

## Recovery Procedures

### AudioContext Suspended (most common)

Browsers require user gesture before audio playback. Pattern:

```typescript
const resumeAudio = async () => {
  if (audioContext.state === 'suspended') {
    await audioContext.resume();
  }
};
// Attach to first user click/tap
document.addEventListener('click', resumeAudio, { once: true });
```

### WebGL Context Lost

```typescript
canvas.addEventListener('webglcontextlost', (e) => {
  e.preventDefault();
  // Pause animation loop
  cancelAnimationFrame(frameId);
  showRecoveryUI('WebGL context lost. Attempting recovery...');
});

canvas.addEventListener('webglcontextrestored', () => {
  // Re-initialize renderer, recompile shaders
  initRenderer();
  showRecoveryUI(null);
});
```

### Shader Compilation Failure

```typescript
const material = new THREE.ShaderMaterial({ vertexShader, fragmentShader });
// Three.js logs shader errors to console
// Fallback: use MeshStandardMaterial with emissive
if (renderer.info.programs?.some(p => p.diagnostics?.error)) {
  material = new THREE.MeshStandardMaterial({
    color: '#00f5ff',
    emissive: '#00f5ff',
    emissiveIntensity: 0.5,
  });
}
```

### Browser-Specific Workarounds

| Browser | Issue | Workaround |
|---|---|---|
| Safari | `AnalyserNode.getFloatTimeDomainData` may return all zeros | Use `getByteTimeDomainData` and convert |
| Safari | `AudioContext` sample rate locked to 44100 | Accept default, adjust FFT bin calculations |
| Firefox | GLSL `precision` differences | Always declare `precision mediump float;` in fragment shaders |
| Mobile Chrome | Audio requires user gesture + `<audio>` element | Use `MediaElementSource`, not `AudioBuffer` |

## Error Logging

All errors append to structured log:

```json
{
  "timestamp": "ISO8601",
  "error_type": "audio_context | audio_source | webgl | performance | memory | file_io | browser",
  "operation": "init_audio | render_frame | load_file | compile_shader",
  "message": "Human-readable description",
  "recoverable": true,
  "retry_count": 0,
  "resolution": "recovered | degraded | failed_permanent",
  "browser": "Chrome 120",
  "gpu": "NVIDIA GeForce RTX 3070"
}
```

## Graceful Degradation

When errors are unrecoverable, degrade in stages:

```
Full 3D Visualizer
    ↓ (WebGL context lost, not restored)
2D Canvas Fallback (frequency bars + waveform)
    ↓ (Canvas fails)
CSS-only Visualizer (div bars with CSS animations)
    ↓ (Everything fails)
Static UI with audio playback only
```

Each degradation level maintains audio playback — the music never stops.
