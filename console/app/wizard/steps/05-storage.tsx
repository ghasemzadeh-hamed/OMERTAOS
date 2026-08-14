'use client';

import { useEffect, useState } from 'react';

type Disk = { name: string; size: string; type: string; mountpoint?: string | null };

type ProbeResponse = { disks?: Disk[] };

export default function Storage() {
  const [disks, setDisks] = useState<Disk[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch('/api/installer/hw')
      .then((res) => res.json())
      .then((data: ProbeResponse) => {
        setDisks(Array.isArray(data?.disks) ? data.disks : []);
        setLoading(false);
      })
      .catch(() => {
        setError('Unable to load disks');
        setLoading(false);
      });
  }, []);

  return (
    <div>
      <h3>Disks</h3>
      {loading && <p>Loading hardware inventory...</p>}
      {error && <p>{error}</p>}
      {!loading && !error && <pre>{JSON.stringify(disks, null, 2)}</pre>}
      <p>Partitioning plan will be preview-only unless running in kiosk+root.</p>
    </div>
  );
}
