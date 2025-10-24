# State Management Map

```mermaid
stateDiagram-v2
  [*] --> Unauthenticated
  Unauthenticated --> Authenticating: Credentials
  Authenticating --> Unauthenticated: Failure
  Authenticating --> Authenticated: Success
  Authenticated --> Dashboard
  state Dashboard {
    [*] --> Loading
    Loading --> Ready
    Ready --> Ready: Optimistic updates
    Ready --> Error: Rate limit
    Error --> Ready: Retry
  }
```
