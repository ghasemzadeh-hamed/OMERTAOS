# UI Redirect Test Matrix

> Runtime alignment: Python control-plane delegates OS-level execution/isolation/sandbox to Rust `runtime-daemon` over gRPC (`shared/proto/runtime.proto`).


## Local Web Console

| State | Expected Path |
| --- | --- |
| setup=false | /setup |
| setup=true, unauthenticated | /login |
| setup=true, authenticated, onboarding=false | /onboarding |
| setup=true, authenticated, onboarding=true | / |
| health view | /status |

## Native TUI

The native TUI reads the same registry; navigation labels and dashboard widgets should match the web console output shown on launch.
