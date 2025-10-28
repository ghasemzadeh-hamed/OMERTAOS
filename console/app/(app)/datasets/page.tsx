'use client';

import ExcelUpload from '../../../components/datasets/ExcelUpload';

export default function DatasetsPage() {
  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-semibold text-white">Datasets</h1>
        <p className="text-sm text-slate-300">
          Upload Excel → Infer Schema → Map Columns → Commit → (Optional) Train
        </p>
      </div>
      <ExcelUpload />
    </div>
  );
}
