import { SnipLogo } from "@/components/snip-logo";

export function FullPageLoader() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-background">
      <SnipLogo size={40} className="animate-pulse text-primary" />
      <p className="text-sm text-muted-foreground">Loading...</p>
    </div>
  );
}
