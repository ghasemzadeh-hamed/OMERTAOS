import React from 'react';

const diagram = `+-----------------------------+
|  Windows Agent (Copilot)    |
+--------------+--------------+
               |
               |  MCP over stdio
               v
+-----------------------------+
|  ODR (MCP registry/launcher)|
+--------------+--------------+
               |
               |  command = wsl.exe ...
               v
+-----------------------------+
|  WSL2                       |
|  OMERTA MCP Bridge (Node)   |
+--------------+--------------+
               |
               |  HTTP (local)
               v
+------------------+   +------------------+
| OMERTA Gateway   |   | OMERTA Control   |
+------------------+   +------------------+`;

const About: React.FC = () => (
  <div>
    <h2>About OMERTAOS Windows Agentic Bridge</h2>
    <p>Minimal console for configuring and monitoring the OMERTA MCP bridge running inside WSL.</p>
    <pre style={{ background: '#0f172a', color: '#e2e8f0', padding: '1rem', overflowX: 'auto' }}>{diagram}</pre>
  </div>
);

export default About;
