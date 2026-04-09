# E2E Test Conventions (Playwright)

Applies to: `apps/e2e/`

## Page Object Model

Abstract `BasePage` class provides the foundation:

```typescript
abstract class BasePage {
    abstract path: string;

    async navigate(): Promise<void> { ... }
    abstract waitForLoad(): Promise<void>;
    abstract expectOnPage(): Promise<void>;
}
```

Each page has a concrete Page Object in `tests/e2e/base/`:

```typescript
class LinksPage extends BasePage {
    path = "/links";

    async waitForLoad() {
        await this.page.waitForLoadState("networkidle");
    }

    async expectOnPage() {
        await expect(this.page).toHaveURL(/.*\/links/);
    }
}
```

## Test Organization

```
apps/e2e/
  tests/
    setup/             # Auth setup (Clerk integration)
    e2e/               # Standard E2E tests
      base/            # Page Objects
    system/            # System-level tests (deployed environments)
    types/             # Shared test types
```

## Patterns

- Use `networkidle` for `waitForLoad`
- Use role-based selectors: `getByRole`, `getByPlaceholder`, `getByText`
- Clerk auth integration via `@clerk/testing`
- Spec files: `<feature>.spec.ts`
- Page Objects: `<Feature>Page.ts`

## Running

```bash
make e2e:test          # Run all E2E tests
make e2e:test:headed   # Run with browser visible
```
