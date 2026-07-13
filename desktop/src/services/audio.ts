/**
 * Push-to-talk microphone recording and TTS playback, wrapped around the
 * browser MediaRecorder / Audio APIs available inside the Electron renderer.
 */
export class MicrophoneUnavailableError extends Error {}

export class AudioRecorder {
  private mediaRecorder: MediaRecorder | null = null;
  private chunks: BlobPart[] = [];
  private stream: MediaStream | null = null;

  async start(deviceId?: string): Promise<void> {
    if (!navigator.mediaDevices?.getUserMedia) {
      throw new MicrophoneUnavailableError('This environment does not support microphone access.');
    }

    try {
      this.stream = await navigator.mediaDevices.getUserMedia({
        audio: deviceId ? { deviceId: { exact: deviceId } } : true,
      });
    } catch (error) {
      throw new MicrophoneUnavailableError(
        error instanceof Error && error.name === 'NotFoundError'
          ? 'No microphone was found.'
          : 'Microphone permission was denied.'
      );
    }

    this.chunks = [];
    this.mediaRecorder = new MediaRecorder(this.stream);
    this.mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) this.chunks.push(event.data);
    };
    this.mediaRecorder.start();
  }

  stop(): Promise<Blob> {
    return new Promise((resolve, reject) => {
      if (!this.mediaRecorder) {
        reject(new Error('Recording was not started.'));
        return;
      }
      this.mediaRecorder.onstop = () => {
        const blob = new Blob(this.chunks, { type: 'audio/webm' });
        this.stream?.getTracks().forEach((track) => track.stop());
        this.stream = null;
        this.mediaRecorder = null;
        resolve(blob);
      };
      this.mediaRecorder.stop();
    });
  }

  cancel(): void {
    this.mediaRecorder?.stop();
    this.stream?.getTracks().forEach((track) => track.stop());
    this.stream = null;
    this.mediaRecorder = null;
    this.chunks = [];
  }

  static async listInputDevices(): Promise<MediaDeviceInfo[]> {
    if (!navigator.mediaDevices?.enumerateDevices) return [];
    const devices = await navigator.mediaDevices.enumerateDevices();
    return devices.filter((d) => d.kind === 'audioinput');
  }

  static async listOutputDevices(): Promise<MediaDeviceInfo[]> {
    if (!navigator.mediaDevices?.enumerateDevices) return [];
    const devices = await navigator.mediaDevices.enumerateDevices();
    return devices.filter((d) => d.kind === 'audiooutput');
  }
}

export class SpeechPlayer {
  private audio: HTMLAudioElement | null = null;

  async play(blob: Blob, onEnded?: () => void): Promise<void> {
    this.stop();
    const url = URL.createObjectURL(blob);
    this.audio = new Audio(url);
    this.audio.onended = () => {
      URL.revokeObjectURL(url);
      onEnded?.();
    };
    await this.audio.play();
  }

  stop(): void {
    if (this.audio) {
      this.audio.pause();
      this.audio.currentTime = 0;
      this.audio = null;
    }
  }

  get isPlaying(): boolean {
    return !!this.audio && !this.audio.paused;
  }
}
