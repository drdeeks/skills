// trackVertex.glsl
varying vec3 vPosition;
varying vec3 vNormal;
varying vec2 vUv;
varying float vEnergy;

uniform float uTime;
uniform float uBassEnergy;
uniform float uMidEnergy;
uniform float uTrebleEnergy;
uniform float uOverallEnergy;
uniform float uBeatPulse;

void main() {
  vUv = uv;
  vNormal = normalize(normalMatrix * normal);

  vec3 displacedPosition = position;

  float waveX = sin(position.x * 2.0 + uTime * 2.0) * uBassEnergy * 0.15;
  float waveZ = cos(position.z * 1.5 + uTime * 1.5) * uMidEnergy * 0.1;
  float waveY = sin(position.x * 3.0 + position.z * 2.0 + uTime * 3.0) * uTrebleEnergy * 0.05;

  displacedPosition += normal * (waveX + waveZ + waveY);

  float pulseScale = 1.0 + uBeatPulse * 0.02;
  displacedPosition *= pulseScale;

  vPosition = (modelViewMatrix * vec4(displacedPosition, 1.0)).xyz;
  vEnergy = uOverallEnergy;

  gl_Position = projectionMatrix * modelViewMatrix * vec4(displacedPosition, 1.0);
}

// trackFragment.glsl
varying vec3 vPosition;
varying vec3 vNormal;
varying vec2 vUv;
varying float vEnergy;

uniform float uTime;
uniform float uBassEnergy;
uniform float uMidEnergy;
uniform float uTrebleEnergy;
uniform float uOverallEnergy;
uniform float uBeatPulse;
uniform vec3 uBaseColor;
uniform vec3 uGlowColor;
uniform float uSectionHue;

void main() {
  vec3 viewDirection = normalize(-vPosition);
  float fresnel = pow(1.0 - max(dot(viewDirection, vNormal), 0.0), 3.0);

  float gridX = step(0.95, fract(vUv.x * 20.0));
  float gridZ = step(0.95, fract(vUv.y * 10.0 + uTime * 0.5));
  float grid = max(gridX, gridZ) * 0.3;

  float scrollPattern = sin(vUv.x * 30.0 + uTime * 4.0) * 0.5 + 0.5;
  scrollPattern *= sin(vUv.y * 15.0 - uTime * 2.0) * 0.5 + 0.5;
  scrollPattern *= 0.15 * uOverallEnergy;

  vec3 color = uBaseColor;
  color += uGlowColor * fresnel * (0.5 + uBassEnergy * 0.5);
  color += uGlowColor * grid;
  color += vec3(uSectionHue, 0.5, 0.8) * scrollPattern;

  float emissiveIntensity = 0.1 + uOverallEnergy * 0.4 + uBeatPulse * 0.3;
  color += uGlowColor * emissiveIntensity;

  float edgeGlow = smoothstep(0.0, 0.3, vUv.x) * smoothstep(1.0, 0.7, vUv.x);
  color += uGlowColor * (1.0 - edgeGlow) * 0.5;

  gl_FragColor = vec4(color, 0.95);
}
