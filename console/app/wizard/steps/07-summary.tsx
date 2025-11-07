'use client';

export default function Summary() {
  return (
    <div>
      <h3>Summary</h3>
      <p>Review selections before applying changes. Profiles and credentials are written via the installer pipeline.</p>
      <ul>
        <li>Install mode determines whether disk operations are enabled.</li>
        <li>Profile controls services, AI tooling and security posture.</li>
        <li>First boot scripts finalize updates and driver setup.</li>
      </ul>
    </div>
  );
}
