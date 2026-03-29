import { SignIn } from "@clerk/react";
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/")({
  component: LoginPage,
});

function LoginPage() {
  return (
    <div className="flex min-h-[80vh] items-center justify-center">
      <SignIn routing="hash" />
    </div>
  );
}
