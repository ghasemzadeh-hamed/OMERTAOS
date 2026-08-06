# Native profiles

The `lite.env`, `full.env`, and `enterprise.env` files are non-secret overlays
for `/etc/omertaos/omertaos.env`. Optional data services remain disabled until
N3 installs and validates their endpoints; selecting a larger profile must not
silently enable an unavailable dependency.

The YAML files are preserved migration inputs from the former root `config/`
directory. Runtime services do not load them. N2 may translate their resource
limits into installer choices, but the `.env` overlays are the canonical Native
profile names from N1 onward.

