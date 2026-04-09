# Frontend Conventions (React)

Applies to: `apps/dashboard-frontend/`

## File Structure

```
src/
  main.tsx                    # App entry: ClerkProvider, QueryClientProvider, RouterProvider
  globals.css                 # Tailwind imports
  routes/                     # TanStack Router file-based routes (THIN — just import + createFileRoute)
    __root.tsx
    index.tsx
    links.tsx
    dashboard.tsx
    settings.tsx
  pages/                      # Feature pages — all logic lives here
    <Feature>/
      <Feature>Page.tsx       # Main page component
      components/             # Page-specific components
        __tests__/            # Co-located component tests
      hooks/                  # Page-specific custom hooks wrapping useQuery/useMutation
      helpers.ts              # Pure utility functions
      types.ts                # Page-specific types
      __tests__/              # Page-level tests
  components/
    ui/                       # Reusable UI primitives (shadcn/ui style, Radix-based)
    layout/                   # Shell, header, sidebar
    auth/                     # Auth-related (token sync, org guard)
  lib/
    api/                      # API client layer
      BaseApi.ts              # Shared axios instance, abstract base class
      <Resource>Api.ts        # One class per backend resource
      types.ts                # Shared API types (mirrors backend response shapes)
      index.ts                # Singleton instances export
      __tests__/              # API class tests
    utils.ts                  # General utilities (cn, etc.)
    dev-mode.ts               # Dev mode detection
    feature-flags.tsx         # Feature flag context provider
  test/
    setup.ts                  # Vitest setup (@testing-library/jest-dom)
    wrapper.tsx               # TestWrapper with QueryClientProvider
```

## Routing

**TanStack Router** with file-based routing. Route files in `src/routes/` are **thin wrappers**:

```tsx
import { LinksPage } from "@/pages/Links/LinksPage";
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/links")({
    component: LinksPage,
});
```

- **Never** put page logic, data fetching, or state in route files
- Route files only import the page component and create the route
- `routeTree.gen.ts` is auto-generated — do not edit

## API Layer

Abstract `BaseApi` class with typed methods wrapping a shared axios instance:

```typescript
// BaseApi.ts
export abstract class BaseApi {
    protected async get<T>(url: string, params?: object): Promise<T> { ... }
    protected async post<T>(url: string, body?: object): Promise<T> { ... }
    protected async patch<T>(url: string, body?: object): Promise<T> { ... }
    protected async delete(url: string): Promise<void> { ... }
}

// LinksApi.ts
export class LinksApi extends BaseApi {
    async list(page = 1, limit = 20, ...): Promise<LinkListResponse> {
        return this.get<LinkListResponse>("/links", { page, limit, ... });
    }
    async create(body: CreateLinkRequest): Promise<Link> {
        return this.post<Link>("/links", body);
    }
}

// index.ts — singleton instances
export const linksApi = new LinksApi();
export const clicksApi = new ClicksApi();
```

- One API class per backend resource
- Types in `lib/api/types.ts` mirror backend response shapes
- Auth token set globally via `setAuthToken()` — called from auth sync component

## Custom Hooks

Page-specific hooks in `pages/<Feature>/hooks/` wrap TanStack Query:

```typescript
export function useLinks(params: UseLinksParams = {}) {
    const { page = 1, limit = 20, search, sortBy, sortOrder, status } = params;
    return useQuery({
        queryKey: ["links", { page, limit, search, sortBy, sortOrder, status }],
        queryFn: () => linksApi.list(page, limit, search, sortBy, sortOrder, status),
        placeholderData: keepPreviousData,
    });
}
```

- Hook name matches the data: `useLinks`, `useStats`, `useAggregateClicks`
- Include all filter params in `queryKey` for proper cache invalidation
- Use `keepPreviousData` for paginated lists

## Component Patterns

- Function components (no `React.FC`)
- Props defined with `interface`
- No global state library — React context for cross-cutting concerns only (feature flags)
- TanStack Query for all server state

```tsx
interface LinkRowActionsProps {
    link: Link;
    onEdit: (link: Link) => void;
    onDelete: (id: string) => void;
}

function LinkRowActions({ link, onEdit, onDelete }: LinkRowActionsProps) { ... }
```

## Styling

- **Tailwind CSS** with utility classes
- **class-variance-authority** (`cva`) for component variants
- **clsx** + **tailwind-merge** via `cn()` utility from `lib/utils.ts`
- **shadcn/ui**-style primitives in `components/ui/` (Radix-based)
- **lucide-react** for icons

## Testing

- **Vitest** + **Testing Library** + **jsdom**
- Tests co-located in `__tests__/` directories next to the code they test
- Mock API classes with `vi.mock()` and `vi.hoisted()`
- Use `TestWrapper` from `test/wrapper.tsx` for QueryClient context
- Coverage excludes: route files, UI primitives, test utilities, generated files

## Tooling

- **Biome** for linting and formatting (not ESLint/Prettier)
  - Tab indentation
  - Organize imports enabled
  - Ignores: `dist/`, `routeTree.gen.ts`
- **TypeScript** strict mode
- `@` path alias maps to `src/`
- **Vite** for dev server and builds

## Adding a New Page

1. Create `src/pages/<Feature>/<Feature>Page.tsx`
2. Create `src/routes/<feature>.tsx` (thin: import page + `createFileRoute`)
3. Add hooks in `src/pages/<Feature>/hooks/` if data fetching needed
4. Add page-specific components in `src/pages/<Feature>/components/`
5. Add types in `src/pages/<Feature>/types.ts` if needed
