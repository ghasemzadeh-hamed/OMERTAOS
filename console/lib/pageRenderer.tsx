'use client';

import { useEffect, useState } from 'react';
import { callEndpoint } from './endpointClient';
import { orchestratePage, UiContext } from './ai/uiOrchestrator';
import type { PageSchema } from './schemaLoader';

export type RendererProps = {
  schema: PageSchema;
  context: UiContext;
  params?: Record<string, string>;
};

type ComponentProps = {
  component: any;
  data: Record<string, any>;
  onAction?: (action: any, payload?: any) => Promise<void>;
  params?: Record<string, string>;
};

function StatCard({ component, data }: ComponentProps) {
  const value = component.value ?? (component.valueKey ? data?.[component.valueKey] : undefined) ?? '—';
  return (
    <div className="rounded-xl border border-white/10 bg-white/5 p-4 shadow-sm">
      <p className="text-xs uppercase tracking-wide text-white/60">{component.title}</p>
      <p className="text-2xl font-semibold text-white mt-1">{value}</p>
    </div>
  );
}

function Alert({ component }: ComponentProps) {
  const tone = component.variant === 'error' ? 'border-red-500/40 bg-red-900/30 text-red-100' : 'border-cyan-400/30 bg-cyan-900/20 text-cyan-100';
  return (
    <div className={`rounded-lg border ${tone} p-3`}> 
      <p className="font-semibold">{component.title}</p>
      {component.description && <p className="text-sm opacity-90">{component.description}</p>}
    </div>
  );
}

function JsonViewer({ component, data }: ComponentProps) {
  const target = component.dataKey ? data?.[component.dataKey] : component.value;
  return (
    <pre className="whitespace-pre-wrap rounded-lg bg-slate-900/70 p-3 text-xs text-white/80">
      {JSON.stringify(target ?? {}, null, 2)}
    </pre>
  );
}

function Table({ component, data, onAction, params }: ComponentProps) {
  const rows = component.dataKey ? data?.[component.dataKey] ?? [] : [];
  return (
    <div className="overflow-hidden rounded-xl border border-white/10 bg-white/5">
      <table className="w-full text-sm text-white/80">
        <thead className="bg-white/10 text-left text-xs uppercase tracking-wide">
          <tr>
            {component.columns?.map((col: string) => (
              <th key={col} className="px-4 py-2">{col}</th>
            ))}
            {component.rowActions?.length ? <th className="px-4 py-2">Actions</th> : null}
          </tr>
        </thead>
        <tbody>
          {rows.map((row: any, idx: number) => (
            <tr key={row.id ?? idx} className="border-t border-white/5">
              {component.columns?.map((col: string) => (
                <td key={col} className="px-4 py-2">{row[col] ?? '—'}</td>
              ))}
              {component.rowActions?.length ? (
                <td className="px-4 py-2">
                  <div className="flex flex-wrap gap-2">
                    {component.rowActions.map((action: any) => {
                      if (action.type === 'link' && action.hrefTemplate) {
                        const href = action.hrefTemplate.replace('{{id}}', row.id).replace('{id}', row.id);
                        return (
                          <a key={action.id} href={href} className="rounded-md bg-white/10 px-2 py-1 text-xs text-white hover:bg-white/20">
                            {action.label}
                          </a>
                        );
                      }
                      return (
                        <button
                          key={action.id}
                          onClick={() => onAction?.(action, { ...row, ...(params ?? {}) })}
                          className="rounded-md bg-cyan-500/80 px-2 py-1 text-xs text-slate-900 hover:bg-cyan-400"
                        >
                          {action.label}
                        </button>
                      );
                    })}
                  </div>
                </td>
              ) : null}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function Form({ component, onAction }: ComponentProps) {
  const [formState, setFormState] = useState<Record<string, any>>(() => {
    const defaults: Record<string, any> = {};
    for (const field of component.fields ?? []) {
      if (field.default !== undefined) defaults[field.name] = field.default;
    }
    return defaults;
  });

  const handleChange = (name: string, value: any) => {
    setFormState((prev) => ({ ...prev, [name]: value }));
  };

  return (
    <div className="space-y-3">
      {(component.fields ?? []).map((field: any) => (
        <label key={field.name} className="block space-y-1 text-sm text-white/80">
          <span>{field.label ?? field.name}</span>
          {field.type === 'textarea' ? (
            <textarea
              className="w-full rounded-md bg-white/5 p-2"
              placeholder={field.placeholder}
              required={field.required}
              value={formState[field.name] ?? ''}
              onChange={(e) => handleChange(field.name, e.target.value)}
            />
          ) : field.type === 'select' || field.type === 'multiSelect' ? (
            <select
              multiple={field.type === 'multiSelect'}
              className="w-full rounded-md bg-white/5 p-2"
              required={field.required}
              value={formState[field.name] ?? (field.type === 'multiSelect' ? [] : '')}
              onChange={(e) => {
                if (field.type === 'multiSelect') {
                  const selected = Array.from(e.target.selectedOptions).map((o) => o.value);
                  handleChange(field.name, selected);
                } else {
                  handleChange(field.name, e.target.value);
                }
              }}
            >
              {(field.options ?? []).map((opt: string) => (
                <option key={opt} value={opt}>
                  {opt}
                </option>
              ))}
            </select>
          ) : field.type === 'json' ? (
            <textarea
              className="w-full rounded-md bg-white/5 p-2 font-mono"
              placeholder={field.placeholder}
              value={formState[field.name] ?? ''}
              onChange={(e) => handleChange(field.name, e.target.value)}
            />
          ) : (
            <input
              type={field.type === 'password' ? 'password' : field.type === 'number' ? 'number' : 'text'}
              className="w-full rounded-md bg-white/5 p-2"
              placeholder={field.placeholder}
              required={field.required}
              value={formState[field.name] ?? ''}
              onChange={(e) => handleChange(field.name, e.target.value)}
              readOnly={field.readOnly}
            />
          )}
          {field.helpText ? <span className="text-xs text-white/60">{field.helpText}</span> : null}
        </label>
      ))}
      {component.actions?.length ? (
        <div className="flex flex-wrap gap-2">
          {component.actions.map((action: any) => (
            <button
              key={action.id}
              onClick={() => onAction?.(action, formState)}
              className="rounded-md bg-cyan-500/80 px-4 py-2 text-sm font-semibold text-slate-900 hover:bg-cyan-400"
            >
              {action.label}
            </button>
          ))}
        </div>
      ) : null}
    </div>
  );
}

function Steps({ component }: ComponentProps) {
  return (
    <div className="rounded-xl border border-white/10 bg-white/5 p-4">
      <ul className="space-y-2 text-white/80">
        {(component.items ?? []).map((item: any) => (
          <li key={item.id} className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-cyan-400" />
            <span>
              {item.label}
              {item.optional ? ' (optional)' : ''}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}

function renderComponent(component: any, data: Record<string, any>, onAction: any, params?: Record<string, string>) {
  switch (component.type) {
    case 'statCard':
      return <StatCard key={component.id} component={component} data={data} />;
    case 'alert':
      return <Alert key={component.id} component={component} data={data} />;
    case 'jsonViewer':
      return <JsonViewer key={component.id} component={component} data={data} />;
    case 'table':
      return <Table key={component.id} component={component} data={data} onAction={onAction} params={params} />;
    case 'form':
      return <Form key={component.id} component={component} onAction={onAction} data={data} params={params} />;
    case 'steps':
      return <Steps key={component.id} component={component} data={data} />;
    default:
      return null;
  }
}

export default function PageRenderer({ schema, context, params }: RendererProps) {
  const [data, setData] = useState<Record<string, any>>({});
  const [error, setError] = useState<string | null>(null);
  const [working, setWorking] = useState<string | null>(null);
  const [effectiveSchema, setEffectiveSchema] = useState(schema);

  useEffect(() => {
    let cancelled = false;
    orchestratePage(schema, context).then((next) => {
      if (!cancelled) setEffectiveSchema(next);
    });
    return () => {
      cancelled = true;
    };
  }, [schema, context]);

  useEffect(() => {
    let cancelled = false;
    async function fetchData() {
      if (!effectiveSchema.dataSources) return;
      const nextData: Record<string, any> = {};
      for (const source of effectiveSchema.dataSources) {
        try {
          const response = await callEndpoint(source.endpointRef, { tenantId: context.tenantId, params });
          nextData[source.id] = response;
        } catch (err) {
          console.error(err);
          if (!cancelled) setError((err as Error).message);
        }
      }
      if (!cancelled) setData(nextData);
    }
    fetchData();
    return () => {
      cancelled = true;
    };
  }, [effectiveSchema, context.tenancyMode, context.featureFlags, params]);

  const handleAction = async (action: any, payload?: any) => {
    if (action.rbacRoles && !action.rbacRoles.includes(context.role)) {
      setError('You do not have permission to run this action.');
      return;
    }
    if (!action.endpointRef) return;
    setWorking(action.id);
    setError(null);
    try {
      await callEndpoint(action.endpointRef, { payload, tenantId: params?.tenantId, params });
      if (action.successToast) {
        console.info(action.successToast);
      }
    } catch (err) {
      console.error(err);
      setError((err as Error).message);
    } finally {
      setWorking(null);
    }
  };

  return (
    <div className="space-y-6 text-white">
      <header className="space-y-2">
        <h1 className="text-3xl font-semibold">{effectiveSchema.title}</h1>
        <p className="text-white/70">{effectiveSchema.description}</p>
      </header>
      {error ? (
        <div className="rounded-lg border border-red-500/40 bg-red-900/30 p-3 text-sm text-red-100">{error}</div>
      ) : null}
      <div className="space-y-6">
        {(effectiveSchema.sections ?? []).map((section) => (
          <section key={section.id} className="space-y-3">
            <div className="space-y-1">
              <h2 className="text-xl font-semibold">{section.title}</h2>
              {section.helpText ? <p className="text-sm text-white/70">{section.helpText}</p> : null}
            </div>
            <div className="grid gap-3 md:grid-cols-2">
              {(section.components ?? []).map((component: any) => renderComponent(component, data[section.dataKey ?? component.dataKey] ?? data, handleAction, params))}
            </div>
            {section.actions?.length ? (
              <div className="flex flex-wrap gap-2">
                {section.actions.map((action: any) => (
                  <button
                    key={action.id}
                    disabled={working === action.id}
                    onClick={() => handleAction(action, data)}
                    className="rounded-md bg-cyan-500/80 px-4 py-2 text-sm font-semibold text-slate-900 hover:bg-cyan-400 disabled:opacity-50"
                  >
                    {working === action.id ? 'Working…' : action.label}
                  </button>
                ))}
              </div>
            ) : null}
          </section>
        ))}
      </div>
    </div>
  );
}
