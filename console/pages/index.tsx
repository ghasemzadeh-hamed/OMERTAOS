import React from "react";
import RoleBasedLayout from "../components/RoleBasedLayout";
import GovernanceDashboard from "../components/GovernanceDashboard";
import WorkflowDesigner from "../components/WorkflowDesigner";
import AgentCard from "../components/AgentCard";
import ChatPanel from "../personal/ChatPanel";

const HomePage: React.FC = () => {
  return (
    <RoleBasedLayout>
      <div className="grid gap-6 md:grid-cols-2">
        <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="mb-4 text-xl font-semibold">Workflow Designer</h2>
          <WorkflowDesigner />
        </section>
        <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="mb-4 text-xl font-semibold">Governance Overview</h2>
          <GovernanceDashboard />
        </section>
      </div>
      <div className="mt-6 grid gap-6 md:grid-cols-2">
        <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="mb-4 text-xl font-semibold">Agent Catalog</h2>
          <div className="grid gap-4">
            <AgentCard
              name="Research Agent"
              description="Synthesizes knowledge across internal and external sources."
              status="online"
              tags={["research", "analysis"]}
            />
            <AgentCard
              name="Compliance Agent"
              description="Guards policies and tracks audit evidence."
              status="idle"
              tags={["governance", "audit"]}
            />
          </div>
        </section>
        <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="mb-4 text-xl font-semibold">Personal Mode</h2>
          <ChatPanel />
        </section>
      </div>
    </RoleBasedLayout>
  );
};

export default HomePage;
