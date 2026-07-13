import { fireEvent, render, screen } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { ConfirmationModal } from '../src/components/ConfirmationModal';
import { useAssistantStore } from '../src/stores/useAssistantStore';

const initialState = useAssistantStore.getState();

afterEach(() => {
  useAssistantStore.setState(initialState, true);
});

describe('ConfirmationModal', () => {
  it('renders nothing when there is no pending confirmation', () => {
    render(<ConfirmationModal />);
    expect(screen.queryByTestId('confirmation-modal')).not.toBeInTheDocument();
  });

  it('shows the tool name, message, and arguments when a confirmation is pending', () => {
    useAssistantStore.setState({
      pendingConfirmation: {
        confirmationId: 'c-1',
        toolName: 'create_document',
        arguments: { filename: 'notes.md' },
        message: "RIVA is ready to create 'notes.md'.",
      },
    });
    render(<ConfirmationModal />);
    expect(screen.getByText(/create_document/)).toBeInTheDocument();
    expect(screen.getByText("RIVA is ready to create 'notes.md'.")).toBeInTheDocument();
    expect(screen.getByTestId('confirmation-args')).toHaveTextContent('notes.md');
  });

  it('calls confirm(true) when Approve is clicked', () => {
    const confirm = vi.fn();
    useAssistantStore.setState({
      pendingConfirmation: {
        confirmationId: 'c-1',
        toolName: 'create_document',
        arguments: {},
        message: 'Create it?',
      },
      confirm,
    });
    render(<ConfirmationModal />);
    fireEvent.click(screen.getByTestId('approve-button'));
    expect(confirm).toHaveBeenCalledWith(true);
  });

  it('calls confirm(false) when Reject is clicked', () => {
    const confirm = vi.fn();
    useAssistantStore.setState({
      pendingConfirmation: {
        confirmationId: 'c-1',
        toolName: 'create_document',
        arguments: {},
        message: 'Create it?',
      },
      confirm,
    });
    render(<ConfirmationModal />);
    fireEvent.click(screen.getByTestId('reject-button'));
    expect(confirm).toHaveBeenCalledWith(false);
  });
});
