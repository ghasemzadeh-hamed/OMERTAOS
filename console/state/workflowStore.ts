import { create } from "zustand";

export type Stage = {
  id: string;
  name: string;
  description: string;
};

type WorkflowState = {
  stages: Stage[];
  addStage: (stage: Stage) => void;
  removeStage: (id: string) => void;
  reorderStage: (sourceId: string, targetId: string) => void;
};

export const useWorkflowStore = create<WorkflowState>((set) => ({
  stages: [
    { id: "stage-discovery", name: "Discovery", description: "Collect requirements" },
    { id: "stage-execute", name: "Execute", description: "Trigger agent workflows" },
  ],
  addStage: (stage) =>
    set((state) => ({
      stages: [...state.stages, stage],
    })),
  removeStage: (id) =>
    set((state) => ({
      stages: state.stages.filter((stage) => stage.id !== id),
    })),
  reorderStage: (sourceId, targetId) =>
    set((state) => {
      const stages = [...state.stages];
      const sourceIndex = stages.findIndex((item) => item.id === sourceId);
      const targetIndex = stages.findIndex((item) => item.id === targetId);
      if (sourceIndex === -1 || targetIndex === -1) {
        return { stages };
      }
      const [removed] = stages.splice(sourceIndex, 1);
      stages.splice(targetIndex, 0, removed);
      return { stages };
    }),
}));
