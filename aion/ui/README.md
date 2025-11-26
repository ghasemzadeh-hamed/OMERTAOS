# AION Catalog UI

This directory holds the planned Next.js implementation of the catalog surfaces (Grid, ToolView, Editor, Chat Assistant). The frontend code is not present here, but the backend APIs, configuration, and worker synchronization layers that serve the UI are ready.

Key integrations:

- Catalog APIs live in [`aion/control/catalog_api.py`](../control/catalog_api.py) and surface agent and tool metadata to the console.
- Catalog sync workers run from [`aion/worker/catalog_sync.py`](../worker/catalog_sync.py) to keep the database aligned with registry and recipe files.
- UI wiring in [`aion/config/aion.yaml`](../config/aion.yaml) and [`aion/docker/compose.catalog.yml`](../docker/compose.catalog.yml) exposes the catalog services over HTTP when the compose profile is enabled.

When adding the React/Next.js code, point API calls to the gateway or control endpoints described above so the UI stays aligned with the existing catalog and worker logic.

---

##

#

     Next.js    (Grid ToolView Editor Chat Assistant) .         API            .

 :

- API   [`aion/control/catalog_api.py`](../control/catalog_api.py)            .
-     [`aion/worker/catalog_sync.py`](../worker/catalog_sync.py)             .
-    [`aion/config/aion.yaml`](../config/aion.yaml)  [`aion/docker/compose.catalog.yml`](../docker/compose.catalog.yml)     compose      HTTP    .

   React/Next.js  API                     .
