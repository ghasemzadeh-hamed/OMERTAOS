# Release process

## Versioning

- Follow semantic versioning (`MAJOR.MINOR.PATCH`).
- Tag releases in git (`git tag v1.2.0`).
- Publish change logs covering installer, kernel, and UI updates.

## SBOM

1. Run `scripts/sbom.sh` to generate CycloneDX output for Node, Python, and system packages.
2. Store SBOM artifacts alongside the release assets.

## Signing

1. Sign ISO images with `cosign sign-blob` or your preferred GPG tooling.
2. Provide signatures and SHA256 checksums in the release notes.
3. Verify signatures during smoke tests before publishing.

## Validation

- Execute the acceptance matrix: ISO, native, WSL, Docker.
- Test GPU coverage (NVIDIA, AMD, Intel) and NIC coverage (Intel, Realtek, Mellanox).
- Confirm first boot logs show completed security tasks.

## Publication

- Upload artifacts to your release bucket or portal.
- Update documentation links if URLs changed.
- Announce availability in the internal release channel.
