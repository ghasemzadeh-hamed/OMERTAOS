import React from "react";

type AgentCardProps = {
  name: string;
  description: string;
  status: "online" | "idle" | "offline";
  tags?: string[];
};

const statusColor: Record<AgentCardProps["status"], string> = {
  online: "bg-green-500",
  idle: "bg-amber-500",
  offline: "bg-slate-400",
};

const AgentCard: React.FC<AgentCardProps> = ({ name, description, status, tags = [] }) => {
  return (
    <article className="rounded border border-slate-200 bg-white p-4 shadow-sm">
      <header className="mb-2 flex items-center justify-between">
        <h3 className="text-lg font-semibold text-slate-800">{name}</h3>
        <span className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold text-white ${statusColor[status]}`}>
          {status.toUpperCase()}
        </span>
      </header>
      <p className="text-sm text-slate-600">{description}</p>
      {tags.length > 0 && (
        <ul className="mt-3 flex flex-wrap gap-2 text-xs">
          {tags.map((tag) => (
            <li key={tag} className="rounded-full bg-slate-100 px-2 py-1 text-slate-700">
              #{tag}
            </li>
          ))}
        </ul>
      )}
    </article>
  );
};

export default AgentCard;
