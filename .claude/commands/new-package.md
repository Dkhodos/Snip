---
name: new-package
description: Scaffold a new shared package following the Provider Pattern
---

# Scaffold New Shared Package

Create a new shared package following the conventions in `.claude/rules/package-conventions.md`.

## Instructions

1. Ask the user for:
   - **Package name** (single word or hyphenated, e.g., `cache`, `rate-limit`)
   - **Purpose** (one-line description)
   - **Providers** (e.g., `redis, dev` or `stripe, dev`) — `dev` is always included

2. Derive names:
   - Directory: `packages/<name>/`
   - pip name: `<project>-<name>`
   - Import name: `<project>_<name>`

3. Create the following files:

```
packages/<name>/
  src/<project>_<name>/
    __init__.py          # Public API with __all__
    protocol.py          # typing.Protocol for client interface + frozen dataclass DTOs
    provider.py          # StrEnum with DEV + real providers
    factory.py           # create_<name>_client() factory returning Protocol type
    exceptions.py        # Package-specific exceptions (if needed)
    providers/
      __init__.py
      dev/
        __init__.py
        client.py        # Dev/test implementation
      <real_provider>/
        __init__.py
        client.py        # Real implementation (stub with NotImplementedError)
  tests/
    __init__.py
    conftest.py
    unit/
      __init__.py
      test_factory.py    # Test factory creates correct client types
  pyproject.toml         # <project>-<name>, hatchling build, same ruff/pyright config
  Makefile               # Same pattern as other packages
```

4. Add `<name>:packages/<name>` to root `Makefile` PROJECTS list
5. Run `uv sync --all-packages`
6. Run `make <name>:lint` to verify

## Reference

Use `packages/auth/` as the canonical example of the Provider Pattern. For simpler packages without providers (like the logger package), skip the providers directory and factory.
