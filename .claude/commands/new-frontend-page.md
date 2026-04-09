---
name: new-frontend-page
description: Scaffold a new frontend page with route, hooks, and components
---

# Scaffold New Frontend Page

Create a new page following the conventions in `.claude/rules/frontend-conventions.md`.

## Instructions

1. Ask the user for:
   - **Page name** (PascalCase, e.g., `Billing`, `UserSettings`)
   - **Route path** (e.g., `/billing`, `/settings/users`)

2. Create the following files:

```
apps/dashboard-frontend/src/
  pages/<PageName>/
    <PageName>Page.tsx       # Main page component
    components/              # (empty dir — will hold page-specific components)
    hooks/                   # (empty dir — will hold custom hooks)
    types.ts                 # Page-specific types (if needed)
    __tests__/
      <PageName>Page.test.tsx  # Basic render test
  routes/<route-path>.tsx    # Thin route file
```

3. Route file pattern (MUST be thin):
```tsx
import { <PageName>Page } from "@/pages/<PageName>/<PageName>Page";
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/<route-path>")({
    component: <PageName>Page,
});
```

4. Page component pattern:
```tsx
export function <PageName>Page() {
    return (
        <div>
            <h1><PageName></h1>
        </div>
    );
}
```

5. Run `npm run build` in `apps/dashboard-frontend/` to regenerate `routeTree.gen.ts`

## Reference

Use `pages/Links/` as the canonical example of a fully built-out page with components, hooks, helpers, and tests.
