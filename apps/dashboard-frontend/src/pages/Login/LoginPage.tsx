import { SnipLogo } from "@/components/snip-logo";
import { DEV_MODE } from "@/lib/dev-mode";
import { SignIn } from "@clerk/react";
import { Navigate } from "@tanstack/react-router";

export function LoginPage() {
	if (DEV_MODE) {
		return <Navigate to="/dashboard" />;
	}

	return (
		<div className="flex min-h-screen flex-col items-center justify-center gap-6 bg-background p-4">
			<div className="flex items-center gap-2">
				<SnipLogo size={32} className="text-primary" />
				<span className="text-xl font-semibold tracking-tight">Snip</span>
			</div>
			<SignIn routing="hash" forceRedirectUrl="/dashboard" />
		</div>
	);
}
