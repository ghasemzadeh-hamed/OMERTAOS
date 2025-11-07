# Windows Installer Helpers

This directory hosts documentation and PowerShell snippets that integrate
with the shared installer logic under `core/installer`.  The goal is to
keep the Windows bootstrap flow aligned with the Linux and ISO
installers so that all of them call into the same profile and
configuration helpers shipped as part of the `aionos` CLI.
