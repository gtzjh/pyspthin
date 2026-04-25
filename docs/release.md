# Release And Tagging

This repository uses annotated Git tags to mark project versions.

## Version Rule

- Package versions live in `pyproject.toml`.
- Release tags use the format `vMAJOR.MINOR.PATCH`.
- The tag version must match the package version. For example, package version `0.1.0` maps to tag `v0.1.0`.

## Creating A Release Tag

After committing release-ready changes:

```bash
git status --short
git tag -a v0.1.0 -m "pyspthin 0.1.0"
git push origin main
git push origin v0.1.0
```

Pushing a tag triggers the GitHub Actions test workflow, because the workflow runs on every `push`.

## Inspecting Tags

```bash
git tag --list
git show v0.1.0
```
