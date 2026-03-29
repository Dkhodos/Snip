import { createFileRoute } from "@tanstack/react-router";
import { Settings } from "lucide-react";
import { DEV_MODE } from "@/lib/dev-mode";
import { OrgGeneralSettings } from "@/components/org/org-general-settings";
import { OrgMembers } from "@/components/org/org-members";

export const Route = createFileRoute("/settings")({
  component: SettingsPage,
});

function SettingsPage() {
  return (
    <div className="h-full overflow-y-auto">
      <div className="space-y-6">
        <h1 className="text-2xl font-bold">Settings</h1>
        {DEV_MODE ? (
          <div className="rounded-lg border border-border bg-card p-12 text-center">
            <Settings className="mx-auto h-12 w-12 text-muted-foreground" />
            <p className="mt-4 text-muted-foreground">
              Organization settings require Clerk authentication.
            </p>
          </div>
        ) : (
          <>
            <OrgGeneralSettings />
            <OrgMembers />
          </>
        )}
      </div>
    </div>
  );
}
