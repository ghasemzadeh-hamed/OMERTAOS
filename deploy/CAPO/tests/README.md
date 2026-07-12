# CAPO static tests

Run `contract-tests.ps1` from PowerShell to check environment keys, canonical
ports, smoke/rollback contracts, Quickstart exposure, and forbidden destructive
commands. The test is read-only and is suitable for the Windows automation
host. Native systemd acceptance still requires the intended Linux SSD host.
