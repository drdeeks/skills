import { registerAnimationSkill } from '../../../skills/threejs-animation';

export interface AudioAnalyzerResult {
  audioContext: AudioContext;
  analyser: AnalyserNode;
  source: MediaElementAudioSourceNode;
  frequencyData: Uint8Array;
}

export class AudioAnalyzer {
  private audioContext: AudioContext | null = null;
  private analyser: AnalyserNode | null = null;
  private source: MediaElementAudioSourceNode | null = null;
  private animationSkill: any = null;

  async analyzeAudio(audioElement: HTMLAudioElement): Promise<AudioAnalyzerResult> {
    this.audioContext = new AudioContext();
    if (this.audioContext.state === 'suspended') {
      await this.audioContext.resume();
    }

    this.analyser = this.audioContext.createAnalyser();
    this.analyser.fftSize = 2048;
    this.analyser.smoothingTimeConstant = 0.8;

    const audioClone = audioElement.cloneNode() as HTMLAudioElement;
    audioClone.src = audioElement.src;
    audioClone.preload = 'auto';
    audioClone.load();

    await new Promise<void>((resolve, reject) => {
      audioClone.addEventListener('loadeddata', () => resolve(), { once: true });
      audioClone.addEventListener('error', () => reject(new Error('Failed to load audio clone')), { once: true });
      if (audioClone.readyState >= 2) resolve();
    });

    this.source = this.audioContext.createMediaElementSource(audioClone);
    this.source.connect(this.analyser);
    this.analyser.connect(this.audioContext.destination);

    const bufferLength = this.analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    // Initialize threejs-animation skill
    this.animationSkill = registerAnimationSkill({
      register: (skill) => skill,
      get: () => this.animationSkill,
      addUpdateCallback: (callback) => {
        // Add to animation loop
      },
      getActiveMixers: () => []
    }).init(null, null, null, this.audioContext);

    return {
      audioContext: this.audioContext,
      analyser: this.analyser,
      source: this.source,
      frequencyData: dataArray
    };
  }

  /**
   * Syncs an object's property to an audio feature (e.g., bass, treble).
   * @param object - The Three.js object to animate.
   * @param property - Property to animate (e.g., 'scale.x').
   * @param audioFeature - Audio feature to sync to (e.g., 'energy').
   */
  syncToAudio(object: any, property: string, audioFeature: string): void {
    if (!this.animationSkill) return;
    this.animationSkill.syncToAudio(object, property, audioFeature);
  }

  /**
   * Creates a beat-synced pulse effect.
   * @param object - The Three.js object to pulse.
   */
  createBeatPulse(object: any): void {
    if (!this.animationSkill) return;
    this.animationSkill.createBeatPulse(object);
  }
}