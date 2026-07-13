import type { TimelineStep } from '../types';

interface TaskTimelineProps {
  steps: TimelineStep[];
}

export function TaskTimeline({ steps }: TaskTimelineProps) {
  if (steps.length === 0) return null;

  return (
    <div className="timeline" data-testid="task-timeline">
      <div className="panel-title" style={{ marginBottom: 4 }}>
        Current Task
      </div>
      {steps.map((step, index) => (
        <div className="timeline-step" key={`${step.label}-${index}`}>
          {step.label}
          {step.detail ? ` — ${step.detail}` : ''}
        </div>
      ))}
    </div>
  );
}
