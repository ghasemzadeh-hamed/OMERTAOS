import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  scenarios: {
    ramp: {
      executor: 'ramping-arrival-rate',
      startRate: 10,
      timeUnit: '1s',
      preAllocatedVUs: 20,
      stages: [
        { target: 50, duration: '1m' },
        { target: 200, duration: '3m' }
      ]
    }
  }
};

export default function () {
  const payload = JSON.stringify({
    schemaVersion: '1.0',
    intent: 'summarize',
    params: { text: 'load test payload' }
  });
  const res = http.post(`${__ENV.API_URL || 'http://localhost:8080'}/v1/tasks`, payload, {
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': __ENV.API_KEY || 'demo-key'
    }
  });
  check(res, {
    'status is 200': (r) => r.status === 200
  });
  sleep(0.5);
}
