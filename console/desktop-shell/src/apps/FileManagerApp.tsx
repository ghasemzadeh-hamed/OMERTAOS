import { Bot, Folder, FolderCog, Home, ScrollText } from 'lucide-react';

const locations = [
  { label: 'Home', icon: Home },
  { label: 'Projects', icon: FolderCog },
  { label: 'Agents', icon: Bot },
  { label: 'Models', icon: Folder },
  { label: 'Logs', icon: ScrollText },
];

export function FileManagerApp() {
  return (
    <div className="file-app">
      <aside className="file-sidebar">
        <strong>Locations</strong>
        {locations.map(({ label, icon: Icon }, index) => (
          <button className={index === 0 ? 'active' : ''} key={label}><Icon size={17} />{label}</button>
        ))}
      </aside>
      <main className="file-content">
        <div className="empty-illustration"><Folder size={42} /></div>
        <h2>Capability-gated files</h2>
        <p>Filesystem access will become available after Runtime policy and capability integration.</p>
      </main>
    </div>
  );
}
