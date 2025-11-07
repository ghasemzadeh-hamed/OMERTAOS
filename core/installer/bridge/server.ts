import express from 'express';
import { probeHw } from './tasks/disk';
import { applyDrivers } from './tasks/driver';
import { applySecurity } from './tasks/security';

const app = express();
app.use(express.json());

function isRoot() {
  try {
    return typeof process.getuid === 'function' && process.getuid() === 0;
  } catch (error) {
    return false;
  }
}

function allowInstall() {
  return Boolean(process.env.AIONOS_ALLOW_INSTALL);
}

app.post('/task', async (req, res) => {
  const { task, payload } = req.body || {};
  try {
    if (task === 'probe.hw') {
      return res.json(await probeHw());
    }
    if (task === 'plan.partition') {
      return res.json({ plan: 'preview-only', payload });
    }
    if (task === 'apply.partition') {
      if (!(isRoot() && allowInstall())) {
        throw new Error('not-allowed');
      }
      return res.json({ ok: true });
    }
    if (task === 'apply.drivers') {
      if (!isRoot()) {
        throw new Error('root-required');
      }
      return res.json(await applyDrivers());
    }
    if (task === 'apply.security') {
      if (!isRoot()) {
        throw new Error('root-required');
      }
      return res.json(await applySecurity());
    }
    if (task === 'profiles.list') {
      return res.json({ items: ['user', 'pro', 'enterprise'] });
    }
    if (task === 'profiles.apply') {
      return res.json({ ok: true, profile: payload?.name });
    }
    return res.status(404).json({ error: 'unknown-task' });
  } catch (error) {
    const message = error instanceof Error ? error.message : 'bridge-error';
    return res.status(500).json({ error: message });
  }
});

app.listen(3030, () => {
  // eslint-disable-next-line no-console
  console.log('AIONOS bridge :3030');
});
