# Retired pre-canonical tests

These tests targeted Python namespaces and feature implementations that were
not present after the canonical Structure migration (`os.control`, `os.kernel`,
the former CLI bundle, and LatentBox). They are retained as historical evidence
instead of being silently skipped by the active test suite.

Reintroducing any covered feature requires a new test against its canonical
owner; these files must not be restored as active tests by recreating legacy
packages.
