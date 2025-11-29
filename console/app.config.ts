export const appConfig = {
  websocketUrl: process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:3000/ws",
  apiBaseUrl: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  featureFlags: {
    governanceDashboard: true,
    workflowDesigner: true,
    personalMode: true,
  },
};
