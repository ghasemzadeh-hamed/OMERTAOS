export const appConfig = {
  websocketUrl: process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:3000/ws",
  apiBaseUrl: process.env.NEXT_PUBLIC_GATEWAY_URL || "http://localhost:8080",
  featureFlags: {
    governanceDashboard: true,
    workflowDesigner: true,
    personalMode: true,
  },
};
