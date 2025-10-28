'use client';

import { useEffect, useMemo, useState } from 'react';
import { toast } from 'sonner';

interface InferResponse {
  columns: string[];
  types: Record<string, 'string' | 'number' | 'date' | 'boolean' | 'unknown'>;
  sample: Array<Record<string, unknown>>;
  suggestions: Record<string, string[]>;
}

const TARGET_FIELDS = [
  'customer_id',
  'customer_name',
  'sku',
  'product_name',
  'quantity',
  'unit_price',
  'amount',
  'currency',
  'invoice_no',
  'order_date',
  'ship_date',
  'city',
  'region',
  'notes',
] as const;

type TargetField = (typeof TARGET_FIELDS)[number];

type MappingState = Record<string, TargetField | ''>;

const CONTROL_BASE = process.env.NEXT_PUBLIC_CONTROL_URL ?? 'http://localhost:9000';

export default function ExcelUpload() {
  const [file, setFile] = useState<File | null>(null);
  const [tenantId, setTenantId] = useState('tenant-0');
  const [datasetName, setDatasetName] = useState(() => `dataset_${Date.now()}`);
  const [infer, setInfer] = useState<InferResponse | null>(null);
  const [mapping, setMapping] = useState<MappingState>({});
  const [isInferring, setIsInferring] = useState(false);
  const [isApplying, setIsApplying] = useState(false);
  const [datasetId, setDatasetId] = useState<string | null>(null);
  const [trainProfile, setTrainProfile] = useState<'lora' | 'ft_api'>('lora');
  const [trainBudget, setTrainBudget] = useState('');
  const [isTriggeringTrain, setIsTriggeringTrain] = useState(false);
  const [jobId, setJobId] = useState<string | null>(null);

  useEffect(() => {
    if (typeof window === 'undefined') {
      return;
    }
    const stored = window.localStorage.getItem('tenant_id');
    if (stored) {
      setTenantId(stored);
    }
  }, []);

  const sampleHeaders = useMemo(() => {
    if (!infer || infer.sample.length === 0) {
      return [] as string[];
    }
    return Object.keys(infer.sample[0] ?? {});
  }, [infer]);

  async function handleInfer() {
    if (!file) {
      toast.error('Select an Excel file first.');
      return;
    }
    setIsInferring(true);
    setDatasetId(null);
    setJobId(null);
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('tenant_id', tenantId);

      const response = await fetch(`${CONTROL_BASE}/api/ingest/excel/infer`, {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) {
        const detail = await response.text();
        throw new Error(detail || 'Infer request failed');
      }
      const payload = (await response.json()) as InferResponse;
      setInfer(payload);
      const autoMap: MappingState = {};
      payload.columns.forEach((column) => {
        const suggestion = payload.suggestions[column]?.[0];
        autoMap[column] = (suggestion as TargetField | undefined) ?? '';
      });
      setMapping(autoMap);
      toast.success('Schema inferred successfully.');
    } catch (error) {
      console.error(error);
      toast.error('Failed to infer schema.');
    } finally {
      setIsInferring(false);
    }
  }

  async function handleApply() {
    if (!infer) {
      toast.error('Infer the schema before committing.');
      return;
    }
    setIsApplying(true);
    setJobId(null);
    try {
      const response = await fetch(`${CONTROL_BASE}/api/ingest/excel/apply-mapping`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          tenant_id: tenantId,
          dataset_name: datasetName,
          mapping,
          options: { writeMode: 'append' },
        }),
      });
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload?.detail || 'Commit failed');
      }
      setDatasetId(payload.dataset_id);
      toast.success(`Dataset committed (ID: ${payload.dataset_id}).`);
    } catch (error) {
      console.error(error);
      toast.error('Failed to commit dataset.');
    } finally {
      setIsApplying(false);
    }
  }

  async function handleTriggerTrain() {
    if (!datasetId) {
      toast.error('Commit a dataset before triggering training.');
      return;
    }
    setIsTriggeringTrain(true);
    try {
      const body: Record<string, unknown> = {
        tenant_id: tenantId,
        dataset_id: datasetId,
        profile: trainProfile,
      };
      if (trainBudget.trim().length > 0) {
        const parsed = Number(trainBudget);
        if (!Number.isNaN(parsed)) {
          body.budget_usd = parsed;
        }
      }
      const response = await fetch(`${CONTROL_BASE}/api/ingest/excel/trigger-train`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body),
      });
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload?.detail || 'Training trigger failed');
      }
      setJobId(payload.job_id);
      toast.success('Training job queued successfully.');
    } catch (error) {
      console.error(error);
      toast.error('Failed to trigger training.');
    } finally {
      setIsTriggeringTrain(false);
    }
  }

  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-3">
        <div className="glass-card p-5">
          <label className="text-sm font-medium text-slate-200">Excel file (.xlsx)</label>
          <input
            type="file"
            accept=".xlsx,.xls"
            onChange={(event) => setFile(event.target.files?.[0] ?? null)}
            className="mt-3 w-full text-sm text-slate-200"
          />
          <button
            onClick={handleInfer}
            disabled={isInferring || !file}
            className="mt-4 w-full rounded-xl border border-white/20 bg-white/10 px-4 py-2 text-sm font-medium text-white transition hover:bg-white/20 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {isInferring ? 'Inferring…' : 'Infer schema'}
          </button>
        </div>
        <div className="glass-card p-5">
          <label className="text-sm font-medium text-slate-200">Dataset name</label>
          <input
            value={datasetName}
            onChange={(event) => setDatasetName(event.target.value)}
            className="mt-3 w-full rounded-xl border border-white/20 bg-slate-950/40 px-3 py-2 text-sm text-white shadow-inner focus:border-cyan-300 focus:outline-none"
          />
          <p className="mt-2 text-xs text-slate-400">Tenant: {tenantId}</p>
          <button
            onClick={handleApply}
            disabled={isApplying || !infer}
            className="mt-4 w-full rounded-xl border border-emerald-300/30 bg-emerald-500/10 px-4 py-2 text-sm font-medium text-emerald-100 transition hover:bg-emerald-500/20 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {isApplying ? 'Committing…' : 'Commit dataset'}
          </button>
        </div>
        {datasetId ? (
          <div className="glass-card p-5">
            <h3 className="text-sm font-semibold text-slate-100">Dataset committed</h3>
            <p className="mt-1 text-xs text-slate-300">ID: {datasetId}</p>
            {jobId ? (
              <p className="mt-1 text-xs text-emerald-300">Training job: {jobId}</p>
            ) : null}
            <div className="mt-4 space-y-2">
              <label className="text-xs uppercase tracking-wide text-slate-400">Training profile</label>
              <select
                value={trainProfile}
                onChange={(event) => setTrainProfile(event.target.value as 'lora' | 'ft_api')}
                className="w-full rounded-xl border border-white/20 bg-slate-950/40 px-3 py-2 text-sm text-white focus:border-cyan-300 focus:outline-none"
              >
                <option value="lora">LoRA</option>
                <option value="ft_api">Fine-tune API</option>
              </select>
              <input
                type="number"
                step="0.01"
                placeholder="Budget (USD)"
                value={trainBudget}
                onChange={(event) => setTrainBudget(event.target.value)}
                className="w-full rounded-xl border border-white/20 bg-slate-950/40 px-3 py-2 text-sm text-white focus:border-cyan-300 focus:outline-none"
              />
              <button
                onClick={handleTriggerTrain}
                disabled={isTriggeringTrain}
                className="w-full rounded-xl border border-cyan-300/30 bg-cyan-500/10 px-4 py-2 text-sm font-medium text-cyan-100 transition hover:bg-cyan-500/20 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {isTriggeringTrain ? 'Queuing…' : 'Trigger training'}
              </button>
            </div>
          </div>
        ) : (
          <div className="glass-card flex items-center justify-center p-5 text-sm text-slate-400">
            Commit the dataset to unlock training orchestration.
          </div>
        )}
      </div>

      {infer ? (
        <div className="space-y-6">
          <div className="glass-card overflow-x-auto p-5">
            <h3 className="text-sm font-semibold text-slate-100">Sample preview</h3>
            {sampleHeaders.length > 0 ? (
              <table className="mt-3 min-w-full text-left text-xs text-slate-200">
                <thead>
                  <tr className="border-b border-white/10">
                    {sampleHeaders.map((header) => (
                      <th key={header} className="px-3 py-2 font-medium uppercase tracking-wide text-slate-300">
                        {header}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {infer.sample.slice(0, 5).map((row, index) => (
                    <tr key={`row-${index}`} className="border-b border-white/5 last:border-0">
                      {sampleHeaders.map((header) => (
                        <td key={`${index}-${header}`} className="px-3 py-2 text-slate-200">
                          {String((row as Record<string, unknown>)[header] ?? '')}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <p className="mt-3 text-xs text-slate-400">No sample rows available.</p>
            )}
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            {infer.columns.map((column) => (
              <div key={column} className="glass-card p-4">
                <div className="text-xs uppercase tracking-wide text-slate-400">Source column</div>
                <div className="text-sm font-semibold text-slate-100">{column}</div>
                <div className="mt-1 text-xs text-slate-400">Detected type: {infer.types[column]}</div>
                <select
                  value={mapping[column] ?? ''}
                  onChange={(event) =>
                    setMapping((current) => ({ ...current, [column]: event.target.value as TargetField | '' }))
                  }
                  className="mt-3 w-full rounded-xl border border-white/20 bg-slate-950/40 px-3 py-2 text-sm text-white focus:border-cyan-300 focus:outline-none"
                >
                  <option value="">— Not mapped —</option>
                  {TARGET_FIELDS.map((target) => (
                    <option key={target} value={target}>
                      {target}
                    </option>
                  ))}
                </select>
                {infer.suggestions[column]?.length ? (
                  <p className="mt-2 text-xs text-slate-400">
                    Suggestions: {infer.suggestions[column].join(', ')}
                  </p>
                ) : null}
              </div>
            ))}
          </div>
        </div>
      ) : null}
    </div>
  );
}
