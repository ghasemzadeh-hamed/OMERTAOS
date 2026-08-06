# AION Catalog UI

This directory holds the planned Next.js implementation of the catalog surfaces (Grid, ToolView, Editor, Chat Assistant). The frontend code is not present here, but the backend APIs, configuration, and worker synchronization layers that serve the UI are ready.

No standalone catalog deployment is maintained here. When implementing these
surfaces, place product UI in `console/`, call only the Gateway public API, and
read catalog metadata through the canonical Registry and Control boundaries.

---

##

#

     Next.js    (Grid ToolView Editor Chat Assistant) .         API            .

 :

- API calls must cross the Gateway boundary.
- Registry metadata remains under `registry/`.
- Deployment ownership remains under `deploy/`.

   React/Next.js  API                     .
