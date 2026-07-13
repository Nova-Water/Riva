import { useAssistantStore } from '../stores/useAssistantStore';

export function ConfirmationModal() {
  const pending = useAssistantStore((s) => s.pendingConfirmation);
  const confirm = useAssistantStore((s) => s.confirm);

  if (!pending) return null;

  return (
    <div className="modal-overlay" data-testid="confirmation-modal">
      <div className="panel confirmation-modal">
        <h2>Confirmation Required</h2>
        <div className="tool-name">Tool: {pending.toolName}</div>

        <p className="confirmation-message">{pending.message}</p>

        {Object.keys(pending.arguments).length > 0 && (
          <div className="confirmation-args" data-testid="confirmation-args">
            {Object.entries(pending.arguments).map(([key, value]) => (
              <div key={key}>
                <strong>{key}:</strong> {String(value)}
              </div>
            ))}
          </div>
        )}

        <div className="confirmation-impact">
          RIVA will only proceed if you approve. This request expires automatically after a short time.
        </div>

        <div className="confirmation-actions">
          <button className="btn btn-reject" onClick={() => confirm(false)} data-testid="reject-button">
            Reject
          </button>
          <button className="btn btn-approve" onClick={() => confirm(true)} data-testid="approve-button">
            Approve
          </button>
        </div>
      </div>
    </div>
  );
}
