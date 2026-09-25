// Web Audio API and Speech Synthesis engine for NASA Shorts Simulator

class CosmicSoundEngine {
  private ctx: AudioContext | null = null;
  private oscA: OscillatorNode | null = null;
  private oscB: OscillatorNode | null = null;
  private gainA: GainNode | null = null;
  private gainB: GainNode | null = null;
  private masterDroneGain: GainNode | null = null;
  private isDroneActive = false;

  private initCtx() {
    if (!this.ctx) {
      const AudioCtxClass = window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
      if (AudioCtxClass) {
        this.ctx = new AudioCtxClass();
      }
    }
    if (this.ctx && this.ctx.state === 'suspended') {
      this.ctx.resume();
    }
  }

  public startDrone(freqA = 48, freqB = 58, volume = 0.12) {
    try {
      this.initCtx();
      if (!this.ctx) return;

      if (this.isDroneActive) {
        this.updateDroneFrequencies(freqA, freqB);
        return;
      }

      const now = this.ctx.currentTime;
      this.masterDroneGain = this.ctx.createGain();
      this.masterDroneGain.gain.setValueAtTime(0.001, now);
      this.masterDroneGain.gain.exponentialRampToValueAtTime(volume, now + 1.5);
      this.masterDroneGain.connect(this.ctx.destination);

      // Oscillator A (Sub-bass drone)
      this.oscA = this.ctx.createOscillator();
      this.oscA.type = 'sine';
      this.oscA.frequency.setValueAtTime(freqA, now);

      this.gainA = this.ctx.createGain();
      this.gainA.gain.setValueAtTime(0.5, now);
      this.oscA.connect(this.gainA);
      this.gainA.connect(this.masterDroneGain);
      this.oscA.start();

      // Oscillator B (Harmonic drone with slight binaural detune)
      this.oscB = this.ctx.createOscillator();
      this.oscB.type = 'triangle';
      this.oscB.frequency.setValueAtTime(freqB, now);

      this.gainB = this.ctx.createGain();
      this.gainB.gain.setValueAtTime(0.35, now);
      this.oscB.connect(this.gainB);
      this.gainB.connect(this.masterDroneGain);
      this.oscB.start();

      this.isDroneActive = true;
    } catch (e) {
      console.warn('AudioContext not allowed yet:', e);
    }
  }

  public updateDroneFrequencies(freqA: number, freqB: number) {
    if (!this.ctx || !this.isDroneActive) return;
    const now = this.ctx.currentTime;
    if (this.oscA) {
      this.oscA.frequency.exponentialRampToValueAtTime(Math.max(20, freqA), now + 0.8);
    }
    if (this.oscB) {
      this.oscB.frequency.exponentialRampToValueAtTime(Math.max(20, freqB), now + 0.8);
    }
  }

  public stopDrone() {
    if (!this.ctx || !this.isDroneActive) return;
    try {
      const now = this.ctx.currentTime;
      if (this.masterDroneGain) {
        this.masterDroneGain.gain.setValueAtTime(this.masterDroneGain.gain.value, now);
        this.masterDroneGain.gain.exponentialRampToValueAtTime(0.0001, now + 0.8);
      }
      setTimeout(() => {
        try {
          this.oscA?.stop();
          this.oscB?.stop();
          this.oscA?.disconnect();
          this.oscB?.disconnect();
          this.gainA?.disconnect();
          this.gainB?.disconnect();
          this.masterDroneGain?.disconnect();
        } catch {
          // ignore
        }
        this.isDroneActive = false;
      }, 850);
    } catch {
      this.isDroneActive = false;
    }
  }

  public playBoom() {
    try {
      this.initCtx();
      if (!this.ctx) return;
      const now = this.ctx.currentTime;

      // Sub-impact oscillator
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();

      osc.type = 'sine';
      osc.frequency.setValueAtTime(140, now);
      osc.frequency.exponentialRampToValueAtTime(28, now + 1.2);

      gain.gain.setValueAtTime(0.4, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 1.4);

      osc.connect(gain);
      gain.connect(this.ctx.destination);

      osc.start(now);
      osc.stop(now + 1.45);
    } catch {
      // Audio not initiated
    }
  }

  public playWhoosh() {
    try {
      this.initCtx();
      if (!this.ctx) return;
      const now = this.ctx.currentTime;

      const bufferSize = this.ctx.sampleRate * 0.4;
      const buffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
      const data = buffer.getChannelData(0);
      for (let i = 0; i < bufferSize; i++) {
        data[i] = Math.random() * 2 - 1;
      }

      const noise = this.ctx.createBufferSource();
      noise.buffer = buffer;

      const filter = this.ctx.createBiquadFilter();
      filter.type = 'bandpass';
      filter.frequency.setValueAtTime(300, now);
      filter.frequency.exponentialRampToValueAtTime(2200, now + 0.2);
      filter.frequency.exponentialRampToValueAtTime(400, now + 0.4);
      filter.Q.value = 3.5;

      const gain = this.ctx.createGain();
      gain.gain.setValueAtTime(0.01, now);
      gain.gain.linearRampToValueAtTime(0.25, now + 0.15);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.4);

      noise.connect(filter);
      filter.connect(gain);
      gain.connect(this.ctx.destination);

      noise.start(now);
      noise.stop(now + 0.42);
    } catch {
      // Audio not initiated
    }
  }

  public speak(
    text: string,
    options: {
      pitch?: number;
      rate?: number;
      lang?: string;
      onBoundary?: (charIndex: number) => void;
      onEnd?: () => void;
    } = {}
  ): SpeechSynthesisUtterance | null {
    if (!('speechSynthesis' in window)) return null;

    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = options.lang || 'es-ES';
    utterance.rate = options.rate ?? 1.05;
    utterance.pitch = options.pitch ?? 1.0;

    if (options.onBoundary) {
      utterance.onboundary = (event) => {
        if (event.name === 'word') {
          options.onBoundary?.(event.charIndex);
        }
      };
    }

    if (options.onEnd) {
      utterance.onend = () => {
        options.onEnd?.();
      };
    }

    window.speechSynthesis.speak(utterance);
    return utterance;
  }

  public stopSpeaking() {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }
  }
}

export const soundEngine = new CosmicSoundEngine();
