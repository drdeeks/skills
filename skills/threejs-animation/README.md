# Three.js Animation Skill

Handles skeletal, morph target, and keyframe animations for Three.js in **opencode**, **OpenClaw**, and **Hermes**.

## Features
- **AnimationMixer**: Play skeletal/morph animations.
- **KeyframeTrack**: Create custom animations.
- **GSAP Integration**: Smooth transitions (optional).

## Installation
1. Ensure `three` and `gsap` are installed:
   ```bash
   npm install three@^0.160.0 gsap@^3.12.0
   ```
2. Register the skill:
   ```javascript
   import { registerAnimationSkill } from './skills/threejs-animation';
   registerAnimationSkill(skillManager);
   ```

## Usage
### Play an Animation
```javascript
const mixer = skillManager.get('threejs-animation').createMixer(model);
const action = skillManager.get('threejs-animation').playAnimation(mixer, clip);
```

### Create a Custom Keyframe Track
```javascript
const track = skillManager.get('threejs-animation').createKeyframeTrack(
  'position.x',
  [0, 1, 2],
  [0, 5, 0]
);
const clip = new AnimationClip('move', 2, [track]);
```

## Examples
- [Basic Animation](examples/basic.html): Play a GLTF animation.
- [Keyframe Animation](examples/keyframe.html): Custom keyframe tracks.

## Compatibility
- **opencode**: Dynamic skill registration.
- **OpenClaw**: Game entity animations.
- **Hermes**: MCP invocation support.