import { fireEvent, render, screen } from "@testing-library/react";
import WorkflowDesigner from "../../console/components/WorkflowDesigner";

jest.mock("../../console/state/workflowStore", () => {
  const actual = jest.requireActual("../../console/state/workflowStore");
  return {
    ...actual,
    useWorkflowStore: jest.fn().mockImplementation(() => ({
      stages: [
        { id: "stage-1", name: "Stage 1", description: "Desc" },
        { id: "stage-2", name: "Stage 2", description: "Desc" },
      ],
      addStage: jest.fn(),
      removeStage: jest.fn(),
      reorderStage: jest.fn(),
    })),
  };
});

describe("WorkflowDesigner", () => {
  it("renders existing stages", () => {
    render(<WorkflowDesigner />);
    expect(screen.getByText("Stage 1")).toBeInTheDocument();
  });

  it("supports drag and drop reordering", () => {
    const { useWorkflowStore } = jest.requireMock("../../console/state/workflowStore");
    const reorderMock = jest.fn();
    useWorkflowStore.mockImplementation(() => ({
      stages: [
        { id: "stage-1", name: "Stage 1", description: "Desc" },
        { id: "stage-2", name: "Stage 2", description: "Desc" },
      ],
      addStage: jest.fn(),
      removeStage: jest.fn(),
      reorderStage: reorderMock,
    }));
    render(<WorkflowDesigner />);
    const items = screen.getAllByText(/Stage/);
    fireEvent.dragStart(items[0]);
    fireEvent.dragOver(items[1]);
    fireEvent.drop(items[1]);
    expect(reorderMock).toHaveBeenCalled();
  });
});
