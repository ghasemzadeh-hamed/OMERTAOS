'use client';

import { useState } from 'react';

const locales = ['en-US', 'fa-IR', 'de-DE'];

export default function Locale() {
  const [locale, setLocale] = useState('en-US');

  return (
    <div>
      <h2>Select Language</h2>
      <div className="grid">
        {locales.map((item) => (
          <button key={item} onClick={() => setLocale(item)} className={locale === item ? 'sel' : ''}>
            {item}
          </button>
        ))}
      </div>
      <p>Current locale: {locale}</p>
    </div>
  );
}
