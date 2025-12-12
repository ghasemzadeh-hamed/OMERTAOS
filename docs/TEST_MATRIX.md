# UI Redirect Test Matrix

## Local Web Console

| State | Expected Path |
| --- | --- |
| setup=false | /setup |
| setup=true, unauthenticated | /login |
| setup=true, authenticated, onboarding=false | /onboarding |
| setup=true, authenticated, onboarding=true | / |

## Native TUI

The native TUI reads the same registry; navigation labels and dashboard widgets should match the web console output shown on launch.
