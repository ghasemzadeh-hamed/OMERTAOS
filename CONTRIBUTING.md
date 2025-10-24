# Contributing

We welcome contributions from the community.

1. Fork the repository and create a feature branch.
2. Install dependencies:
   - `npm install` in `gateway`
   - `poetry install` in `control`
   - `cargo build` in `modules`
3. Run tests: `npm test`, `poetry run pytest`, and `cargo test`.
4. Ensure JSON schemas and proto files remain backward compatible.
5. Submit a pull request with a clear description and testing evidence.

All contributions are licensed under Apache-2.0.
