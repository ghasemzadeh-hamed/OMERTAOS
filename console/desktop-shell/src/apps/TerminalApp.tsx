export function TerminalApp() {
  return (
    <div className="terminal-app">
      <div className="terminal-toolbar"><span className="terminal-dot" /><span>OMERTA Terminal</span></div>
      <div className="terminal-body" role="log" aria-label="Terminal status">
        <p><span className="terminal-prompt">omerta@local:~$</span> runtime status</p>
        <p>Runtime command execution is disabled until policy and sandbox are connected.</p>
        <p className="terminal-cursor"><span className="terminal-prompt">omerta@local:~$</span> <span /></p>
      </div>
    </div>
  );
}
