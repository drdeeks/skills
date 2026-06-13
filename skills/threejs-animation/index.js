import { AnimationMixer, KeyframeTrack, AnimationClip, LoopRepeat, LoopOnce } from 'three';
import Meyda from 'meyda';
import { detectBeat } from 'web-audio-beat-detector';

/**
 * Registers the threejs-animation skill with opencode/OpenClaw/Hermes.
 * @param {Object} skillManager - The skill manager instance.
 */
export function registerAnimationSkill(skillManager) {
  skillManager.register({
    id: 'threejs-animation',
    init: (scene, camera, renderer, audioContext) => {
      const mixers = new Set();
      let audioAnalyzer = null;
      let beatDetector = null;
      let performanceMode = 'high';

      // Initialize audio analysis if audioContext is provided
      if (audioContext) {
        audioAnalyzer = Meyda.createMeydaAnalyzer({
          audioContext,
          source: audioContext.createMediaElementSource(document.querySelector('audio')),
          bufferSize: 512,
          featureExtractors: ['amplitudeSpectrum', 'rms', 'energy'],
          callback: (features) => {
            if (beatDetector) beatDetector.addToHistory(features.energy);
          }
        });
        beatDetector = detectBeat(audioContext);
      }

      return {
        /**
         * Creates an AnimationMixer for a 3D model.
         * @param {Object3D} model - The Three.js model to animate.
         * @returns {AnimationMixer} The animation mixer.
         */
        createMixer: (model) => {
          const mixer = new AnimationMixer(model);
          mixers.add(mixer);
          return mixer;
        },

        /**
         * Plays an animation clip on a mixer.
         * @param {AnimationMixer} mixer - The animation mixer.
         * @param {AnimationClip} clip - The animation clip to play.
         * @param {Object} [options] - Playback options.
         * @param {number} [options.timeScale=1] - Animation speed.
         * @param {boolean} [options.loop=true] - Whether to loop the animation.
         * @returns {AnimationAction} The animation action.
         */
        playAnimation: (mixer, clip, options = {}) => {
          const action = mixer.clipAction(clip);
          action.timeScale = options.timeScale || 1;
          action.loop = options.loop ? LoopRepeat : LoopOnce;
          action.play();
          return action;
        },

        /**
         * Creates a keyframe track for custom animations.
         * @param {string} name - Track name (e.g., 'position.x').
         * @param {number[]} times - Keyframe times.
         * @param {number[]} values - Keyframe values.
         * @returns {KeyframeTrack} The keyframe track.
         */
        createKeyframeTrack: (name, times, values) => {
          return new KeyframeTrack(name, times, values);
        },

        /**
         * Syncs an object's property to audio features (e.g., bass, treble).
         * @param {Object3D} object - The Three.js object to animate.
         * @param {string} property - Property to animate (e.g., 'scale.x').
         * @param {string} audioFeature - Audio feature to sync to (e.g., 'energy', 'rms').
         * @param {Object} [options] - Sync options.
         * @param {number} [options.min=0.1] - Minimum value.
         * @param {number} [options.max=2] - Maximum value.
         */
        syncToAudio: (object, property, audioFeature, options = {}) => {
          const { min = 0.1, max = 2 } = options;
          const update = () => {
            if (!audioAnalyzer) return;
            const features = audioAnalyzer.get(['energy', 'rms']);
            const value = features[audioFeature] || features.energy;
            const normalized = min + (value * (max - min));
            object[property] = normalized;
          };
          skillManager.addUpdateCallback(update);
        },

        /**
         * Creates a beat-synced pulse effect.
         * @param {Object3D} object - The Three.js object to pulse.
         * @param {Object} [options] - Pulse options.
         * @param {number} [options.scale=1.2] - Pulse scale.
         * @param {number} [options.duration=0.1] - Pulse duration (seconds).
         */
        createBeatPulse: (object, options = {}) => {
          const { scale = 1.2, duration = 0.1 } = options;
          let isPulsing = false;

          const checkBeat = () => {
            if (!beatDetector || isPulsing) return;
            if (beatDetector.isBeat()) {
              isPulsing = true;
              object.scale.set(scale, scale, scale);
              setTimeout(() => {
                object.scale.set(1, 1, 1);
                isPulsing = false;
              }, duration * 1000);
            }
          };
          skillManager.addUpdateCallback(checkBeat);
        },

        /**
         * Adjusts performance settings (e.g., particle count, post-processing).
         * @param {string} mode - Performance mode ('high', 'medium', 'low').
         */
        adjustPerformance: (mode) => {
          performanceMode = mode;
          switch (mode) {
            case 'high':
              renderer.setPixelRatio(window.devicePixelRatio);
              break;
            case 'medium':
              renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5));
              break;
            case 'low':
              renderer.setPixelRatio(1);
              break;
          }
        },

        /**
         * Updates all active mixers (call in animation loop).
         * @param {number} delta - Time delta in seconds.
         */
        update: (delta) => {
          mixers.forEach(mixer => mixer.update(delta));
        }
      };
    }
  });
}