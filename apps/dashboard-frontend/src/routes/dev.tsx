import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createFileRoute, Navigate } from "@tanstack/react-router";
import { Database } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { seedDevData } from "@/lib/api";

const DEV_MODE =
  !import.meta.env.VITE_CLERK_PUBLISHABLE_KEY ||
  import.meta.env.VITE_CLERK_PUBLISHABLE_KEY === "sk_test_...";

export const Route = createFileRoute("/dev")({
  component: DevToolsPage,
});

function DevToolsPage() {
  if (!DEV_MODE) {
    return <Navigate to="/dashboard" />;
  }

  const queryClient = useQueryClient();
  const seedMutation = useMutation({
    mutationFn: seedDevData,
    onSuccess: () => {
      queryClient.invalidateQueries();
    },
  });

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Dev Tools</h1>
      <Card>
        <CardHeader>
          <CardTitle>Seed Database</CardTitle>
          <CardDescription>
            Populate the database with 25 sample links and click events for testing.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button
            onClick={() => seedMutation.mutate()}
            disabled={seedMutation.isPending}
          >
            <Database className="mr-2 h-4 w-4" />
            {seedMutation.isPending ? "Seeding..." : "Seed Data"}
          </Button>
          {seedMutation.isSuccess && (
            <p className="mt-2 text-sm text-muted-foreground">
              Seeded {seedMutation.data.links_created} links with click events.
            </p>
          )}
          {seedMutation.isError && (
            <p className="mt-2 text-sm text-destructive">
              Failed to seed data. Is the backend running?
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
