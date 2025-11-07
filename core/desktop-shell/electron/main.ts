import { app, BrowserWindow } from 'electron';

function createWindow() {
  const window = new BrowserWindow({ width: 1280, height: 800 });
  window.loadURL(process.env.AIONOS_SHELL_URL ?? 'http://localhost:3000/wizard');
}

app.whenReady().then(createWindow);
