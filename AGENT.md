# Agent Instructions

- Create a git tag for every commit before pushing.
- Use an annotated, non-release tag for routine commits, for example
  `commit-YYYYMMDD-<shortsha>`.
- Before creating a release tag, inspect the existing tags first and base the
  new version on the latest `vX.Y.Z` tag.
- Use `vMAJOR.MINOR.PATCH` tags for intentional releases only, and keep the
  `v` prefix on every release tag.
- Bump the version according to the scope of the change:
  - Bug fix or small issue: increment `PATCH` by 1, for example `v0.0.1`.
  - API or interface change: increment `MINOR` by 1, for example `v0.1.0`.
  - Major update: increment `MAJOR` by 1, for example `v1.0.0`.
- These release tags trigger the release workflow and must match the version in
  `pyproject.toml`.
- Push the commit and its tag together.
