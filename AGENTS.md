# Working in The Athenaeum

A public library of standalone notes: book club, interview prep, historical
project planning, and small research experiments. It is not a code repo. This
repo is **public**.

## Start here

- Read [README.md](README.md) for the table of contents. Add new notes there.
- Shared conventions: [home/docs/standards.md](../home/docs/standards.md).

## Rules

- Before committing, run `python scripts/validate_repository.py`. CI runs the
  same check on pull requests and on pushes to `main`.
- `dna-analysis/` holds sensitive personal data. Never read it, quote it, or
  track it. It is gitignored, and the validator fails if anything under it is
  tracked.
- Don't commit symbolic links. The validator rejects them.
- Setup, runbooks, and code for a running system belong in the repo that owns
  that system, not here.

## TODO

- [Dan: add how notes should be written or organized, if you have a
  preference.]
