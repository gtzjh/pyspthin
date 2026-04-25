# Agent Instructions

- Create a git tag for every commit before pushing.
- Use an annotated, non-release tag for routine commits, for example
  `commit-YYYYMMDD-<shortsha>`.
- Reserve `vMAJOR.MINOR.PATCH` tags for intentional releases only. Those tags
  trigger the release workflow and must match the version in `pyproject.toml`.
- Push the commit and its tag together.
