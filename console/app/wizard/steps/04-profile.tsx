'use client';

import { useEffect, useState } from 'react';

type ProfileName = 'user' | 'pro' | 'enterprise';

export default function Profile() {
  const [profile, setProfile] = useState<ProfileName>('user');
  const [profiles, setProfiles] = useState<ProfileName[]>(['user', 'pro', 'enterprise']);

  useEffect(() => {
    fetch('/api/installer/profiles')
      .then((res) => res.json())
      .then((data) => {
        if (Array.isArray(data?.items)) {
          setProfiles(data.items as ProfileName[]);
        }
      })
      .catch(() => {
        setProfiles(['user', 'pro', 'enterprise']);
      });
  }, []);

  return (
    <div>
      <h2>Choose Profile</h2>
      <div className="grid">
        {profiles.map((item) => (
          <button key={item} onClick={() => setProfile(item)} className={profile === item ? 'sel' : ''}>
            {item}
          </button>
        ))}
      </div>
      <small>Profiles affect packages, services and security posture.</small>
    </div>
  );
}
