# Branching strategy

This repository uses a `main`-centric workflow with short-lived topic branches.

## Protected branch

- `main` is the only long-lived branch.
- `main` must stay deployable.
- Changes land in `main` through pull requests after CI passes.

## Topic branch naming

Create branches from `main` using one of these prefixes:

- `feature/<short-description>` for new functionality
- `fix/<short-description>` or `bugfix/<short-description>` for defects
- `security/<short-description>` for security-focused changes
- `hotfix/<short-description>` for urgent production fixes
- `docs/<short-description>` for documentation-only changes
- `chore/<short-description>` for maintenance tasks
- `refactor/<short-description>` for behavior-preserving structural changes
- `test/<short-description>` for test-only changes
- `release/<short-description>` for release preparation work

Use lowercase kebab-case after the prefix, for example:

- `feature/custom-link-aliases`
- `fix/edit-token-validation`
- `chore/update-ci-cache`

Automation branches are allowed for dependency tooling:

- `renovate/...`
- `dependabot/...`

## Merge flow

1. Branch from the latest `main`.
2. Keep the branch focused on one logical change.
3. Rebase on `main` before merging when needed to keep history clean.
4. Merge through a pull request; do not push feature work directly to `main`.

## Repository enforcement

GitHub Actions validates branch names for pushes and pull requests.

Recommended branch protection for `main`:

- require pull requests before merging
- require the `Branch policy` and `CI` checks to pass
- restrict direct pushes
