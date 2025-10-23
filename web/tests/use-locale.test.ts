import { describe, expect, it } from 'vitest';
import en from '../locales/en/common.json';
import fa from '../locales/fa/common.json';

const dictionaries = { en, fa } as const;

describe('i18n dictionaries', () => {
  it('has translations for required keys', () => {
    for (const dict of Object.values(dictionaries)) {
      expect(dict.dashboard.title).toBeTruthy();
      expect(dict.tasks.status.todo).toBeTruthy();
    }
  });
});
