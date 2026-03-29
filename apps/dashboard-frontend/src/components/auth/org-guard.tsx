import { useOrganization } from "@clerk/react";
import type { ReactNode } from "react";
import { DEV_MODE } from "@/lib/dev-mode";
import { SnipLogo } from "@/components/snip-logo";
import { CreateOrgForm } from "@/components/org/create-org-form";
import { FullPageLoader } from "@/components/ui/full-page-loader";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

interface OrgGuardProps {
  children: ReactNode;
}

export function OrgGuard({ children }: OrgGuardProps) {
  if (DEV_MODE) {
    return <>{children}</>;
  }

  return <OrgGuardInner>{children}</OrgGuardInner>;
}

function OrgGuardInner({ children }: OrgGuardProps) {
  const { organization, isLoaded } = useOrganization();

  if (!isLoaded) {
    return <FullPageLoader />;
  }

  if (!organization) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-6 bg-background p-4">
        <div className="flex items-center gap-2">
          <SnipLogo size={32} className="text-primary" />
          <span className="text-xl font-semibold tracking-tight">Snip</span>
        </div>
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle>Create your organization</CardTitle>
            <CardDescription>
              Pick a name and unique slug for your team to get started.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <CreateOrgForm />
          </CardContent>
        </Card>
      </div>
    );
  }

  return <>{children}</>;
}
