import { Bot, Library, MessageSquareText, RadioTower } from 'lucide-react';

const sections = [
  { title: 'Agent Registry', detail: 'Discover installed agent definitions.', icon: Library },
  { title: 'Running Agents', detail: 'No active agent sessions reported.', icon: RadioTower },
  { title: 'Agent Chat', detail: 'Conversation surface is awaiting an API contract.', icon: MessageSquareText },
  { title: 'Agent Templates', detail: 'Reusable templates will appear here.', icon: Bot },
];

export function AgentCenterApp() {
  return (
    <div className="app-page">
      <header className="app-heading">
        <div><span className="section-label">Workspace</span><h2>Agent Center</h2></div>
        <span className="muted">Agent API is not available yet.</span>
      </header>
      <div className="feature-list">
        {sections.map(({ title, detail, icon: Icon }) => (
          <article className="feature-row" key={title}>
            <span className="feature-icon"><Icon size={20} /></span>
            <div><h3>{title}</h3><p>{detail}</p></div>
            <span className="status-text">Not connected</span>
          </article>
        ))}
      </div>
    </div>
  );
}
