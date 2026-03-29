import { RedirectToSignIn, Show } from "@clerk/react";
import { createRootRoute } from "@tanstack/react-router";
import { AppShell } from "@/components/layout/app-shell";
import { FeatureFlagProvider } from "@/lib/feature-flags";

const CLERK_KEY = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY;
const DEV_MODE = !CLERK_KEY || CLERK_KEY === "sk_test_...";

export const Route = createRootRoute({
  component: RootLayout,
});

function RootLayout() {
  if (DEV_MODE) {
    return (
      <FeatureFlagProvider>
        <AppShell />
      </FeatureFlagProvider>
    );
  }

  return (
    <>
      <Show when="signed-out">
        <RedirectToSignIn />
      </Show>
      <Show when="signed-in">
        <FeatureFlagProvider>
          <AppShell />
        </FeatureFlagProvider>
      </Show>
    </>
  );
}
