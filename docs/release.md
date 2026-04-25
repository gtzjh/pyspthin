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

Pushing a tag triggers:

- the test workflow, because it runs on every `push`
- the release workflow, because it runs on tags matching `v*.*.*`

The release workflow validates that the tag version matches `pyproject.toml`, builds the source distribution and wheel, runs `twine check`, uploads the packages as workflow artifacts, and creates a GitHub Release with those package files attached.

Tags with major version `0`, such as `v0.1.0`, are published as GitHub prereleases.

## Publishing An Existing Tag

If a tag already exists before the release workflow was added, run the `Release` workflow manually from GitHub Actions and provide the existing tag name, for example `v0.1.0`.

## Inspecting Tags

```bash
git tag --list
git show v0.1.0
```
