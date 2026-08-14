import React from "react";
import { ShieldCheckIcon } from "@heroicons/react/24/outline";

const metrics = [
  { name: "Policy Coverage", value: "98%", trend: "up" },
  { name: "Audit Events", value: "42", trend: "stable" },
  { name: "Risk Alerts", value: "3", trend: "down" },
];

const GovernanceDashboard: React.FC = () => {
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <ShieldCheckIcon className="h-6 w-6 text-emerald-500" />
        <span className="text-sm text-slate-600">Continuous control monitoring active</span>
      </div>
      <div className="grid gap-3 sm:grid-cols-3">
        {metrics.map((metric) => (
          <div key={metric.name} className="rounded border border-slate-200 bg-slate-50 p-3">
            <p className="text-xs uppercase tracking-wide text-slate-500">{metric.name}</p>
            <p className="text-xl font-semibold text-slate-800">{metric.value}</p>
            <p className="text-xs text-slate-500">Trend: {metric.trend}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default GovernanceDashboard;
