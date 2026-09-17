# Release Process

We release Consulting Intelligence in small, documented phases rather than treating development as one large delivery.

## Versioning

Use semantic versioning:

- `0.x.0` — a phase-level public capability milestone.
- `0.x.y` — a backward-compatible fix or small improvement within that phase.
- `1.0.0` — the first stable, validated product release.

## Release checklist

Before each release:

1. Confirm the phase acceptance criteria are met.
2. Run automated tests and a manual end-to-end check.
3. Update the README, public roadmap, and `CHANGELOG.md`.
4. Add a release note under `docs/releases/` using the template below.
5. Tag the exact Git commit, for example `v0.1.0`.
6. Record known limitations and the next planned phase.

## Release-note template

```md
# v0.x.0 — Phase name

## What users can do

- ...

## Technical highlights

- ...

## Verification

- Automated: ...
- Manual: ...

## Known limitations

- ...

## Next

- ...
```

## Public documentation rule

Public documentation explains the user problem, visible capabilities, setup, verification, and limitations. It must not expose private system architecture, credentials, client data, security controls, internal prompts, or infrastructure configuration.
