import { registerAnimationSkill } from '../../../skills/threejs-animation';

export interface PerformanceProfile {
  quality: 'low' | 'medium' | 'high' | 'ultra';
  maxParticles: number;
  maxTiles: number;
  postProcessingEnabled: boolean;
  shadowEnabled: boolean;
  pixelRatio: number;
  starCount: number;
  floatingObjectCount: number;
}

const PROFILES: Record<string, PerformanceProfile> = {
  low: {
    quality: 'low',
    maxParticles: 100,
    maxTiles: 200,
    postProcessingEnabled: false,
    shadowEnabled: false,
    pixelRatio: 1,
    starCount: 500,
    floatingObjectCount: 5,
  },
  medium: {
    quality: 'medium',
    maxParticles: 300,
    maxTiles: 800,
    postProcessingEnabled: true,
    shadowEnabled: false,
    pixelRatio: Math.min(typeof window !== 'undefined' ? window.devicePixelRatio : 1, 1.5),
    starCount: 1500,
    floatingObjectCount: 10,
  },
  high: {
    quality: 'high',
    maxParticles: 500,
    maxTiles: 1500,
    postProcessingEnabled: true,
    shadowEnabled: true,
    pixelRatio: Math.min(typeof window !== 'undefined' ? window.devicePixelRatio : 1, 2),
    starCount: 3000,
    floatingObjectCount: 20,
  },
  ultra: {
    quality: 'ultra',
    maxParticles: 1000,
    maxTiles: 3000,
    postProcessingEnabled: true,
    shadowEnabled: true,
    pixelRatio: Math.min(typeof window !== 'undefined' ? window.devicePixelRatio : 1, 2),
    starCount: 5000,
    floatingObjectCount: 30,
  },
};

export class PerformanceTuner {
  private currentProfile: PerformanceProfile = PROFILES.medium;
  private animationSkill: any = null;

  constructor() {
    // Initialize threejs-animation skill
    this.animationSkill = registerAnimationSkill({
      register: (skill) => skill,
      get: () => this.animationSkill
    }).init(null, null, { setPixelRatio: (ratio) => {} });
  }

  detectHardware(): PerformanceProfile {
    if (typeof document === 'undefined') return PROFILES.low;
    const canvas = document.createElement('canvas');
    const gl = canvas.getContext('webgl2') || canvas.getContext('webgl');
    if (!gl) return PROFILES.low;

    const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
    const renderer = debugInfo ? gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL) : '';
    const maxTextureSize = gl.getParameter(gl.MAX_TEXTURE_SIZE);

    if (maxTextureSize >= 8192 && renderer.includes('RTX')) {
      return PROFILES.ultra;
    }
    if (maxTextureSize >= 4096 && renderer.includes('GTX')) {
      return PROFILES.high;
    }
    if (maxTextureSize >= 2048) {
      return PROFILES.medium;
    }
    return PROFILES.low;
  }

  setProfile(profile: PerformanceProfile): void {
    this.currentProfile = profile;
    if (this.animationSkill) {
      this.animationSkill.adjustPerformance(profile.quality);
    }
  }

  getProfile(): PerformanceProfile {
    return this.currentProfile;
  }
}

export const performanceTuner = new PerformanceTuner();