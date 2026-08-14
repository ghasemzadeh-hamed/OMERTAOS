'use client';

import React, { useMemo, useState } from "react";
import { useWorkflowStore } from "../state/workflowStore";

const WorkflowDesigner: React.FC = () => {
  const { stages, addStage, removeStage, reorderStage } = useWorkflowStore();
  const [draggingId, setDraggingId] = useState<string | null>(null);
  const canAdd = useMemo(() => stages.length < 10, [stages.length]);

  return (
    <div className="space-y-4">
      <ul className="space-y-2">
        {stages.map((stage) => (
          <li
            key={stage.id}
            draggable
            onDragStart={() => setDraggingId(stage.id)}
            onDragOver={(event) => event.preventDefault()}
            onDrop={() => {
              if (draggingId && draggingId !== stage.id) {
                reorderStage(draggingId, stage.id);
              }
              setDraggingId(null);
            }}
            className="flex items-center justify-between rounded border border-slate-200 bg-slate-50 p-3 shadow-sm"
          >
            <div>
              <p className="text-sm font-medium">{stage.name}</p>
              <p className="text-xs text-slate-500">{stage.description}</p>
            </div>
            <button
              className="rounded bg-red-500 px-3 py-1 text-xs font-semibold text-white hover:bg-red-600"
              onClick={() => removeStage(stage.id)}
            >
              Remove
            </button>
          </li>
        ))}
      </ul>
      <button
        className="rounded bg-blue-600 px-4 py-2 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:bg-blue-200"
        onClick={() =>
          addStage({
            id: `stage-${Date.now()}`,
            name: "New Stage",
            description: "Configure automation actions",
          })
        }
        disabled={!canAdd}
      >
        Add Stage
      </button>
    </div>
  );
};

export default WorkflowDesigner;
