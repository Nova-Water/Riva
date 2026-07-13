import { fireEvent, render, screen } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { InputControls } from '../src/components/InputControls';
import { useAssistantStore } from '../src/stores/useAssistantStore';

const initialState = useAssistantStore.getState();

afterEach(() => {
  useAssistantStore.setState(initialState, true);
});

describe('InputControls microphone states', () => {
  it('shows the idle microphone button when not recording', () => {
    render(<InputControls onOpenSettings={() => {}} />);
    const micButton = screen.getByTestId('mic-button');
    expect(micButton.className).not.toContain('recording');
    expect(screen.queryByTestId('stop-recording-button')).not.toBeInTheDocument();
  });

  it('shows the recording state and cancel button while recording', () => {
    useAssistantStore.setState({ isRecording: true });
    render(<InputControls onOpenSettings={() => {}} />);
    const micButton = screen.getByTestId('mic-button');
    expect(micButton.className).toContain('recording');
    expect(screen.getByTestId('stop-recording-button')).toBeInTheDocument();
  });

  it('displays a microphone error message when present', () => {
    useAssistantStore.setState({ micError: 'No microphone was found.' });
    render(<InputControls onOpenSettings={() => {}} />);
    expect(screen.getByText('No microphone was found.')).toBeInTheDocument();
  });

  it('calls startRecording when the mic button is clicked while idle', () => {
    const startRecording = vi.fn().mockResolvedValue(undefined);
    useAssistantStore.setState({ startRecording });
    render(<InputControls onOpenSettings={() => {}} />);
    fireEvent.click(screen.getByTestId('mic-button'));
    expect(startRecording).toHaveBeenCalled();
  });

  it('calls stopRecordingAndSend when the mic button is clicked while recording', () => {
    const stopRecordingAndSend = vi.fn().mockResolvedValue(undefined);
    useAssistantStore.setState({ isRecording: true, stopRecordingAndSend });
    render(<InputControls onOpenSettings={() => {}} />);
    fireEvent.click(screen.getByTestId('mic-button'));
    expect(stopRecordingAndSend).toHaveBeenCalled();
  });

  it('disables the text input while recording (push-to-talk exclusivity)', () => {
    useAssistantStore.setState({ isRecording: true });
    render(<InputControls onOpenSettings={() => {}} />);
    expect(screen.getByTestId('text-input')).toBeDisabled();
  });
});
