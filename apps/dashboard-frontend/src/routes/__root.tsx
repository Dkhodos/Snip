import { AuthTokenSync } from "@/components/auth/auth-token-sync";
import { OrgGuard } from "@/components/auth/org-guard";
import { AppShell } from "@/components/layout/app-shell";
import { FullPageLoader } from "@/components/ui/full-page-loader";
import { DEV_MODE } from "@/lib/dev-mode";
import { FeatureFlagProvider } from "@/lib/feature-flags";
import { useAuth } from "@clerk/react";
import { Outlet, createRootRoute, useNavigate } from "@tanstack/react-router";
import { useEffect } from "react";

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

	return <AuthenticatedLayout />;
}

function AuthenticatedLayout() {
	const { isLoaded, isSignedIn } = useAuth();
	const navigate = useNavigate();

	useEffect(() => {
		if (isLoaded && !isSignedIn) {
			// Let the index route handle showing SignIn
			return;
		}
		if (isLoaded && isSignedIn && window.location.pathname === "/") {
			navigate({ to: "/dashboard" });
		}
	}, [isLoaded, isSignedIn, navigate]);

	if (!isLoaded) {
		return <FullPageLoader />;
	}

	if (!isSignedIn) {
		return <Outlet />;
	}

	return (
		<>
			<AuthTokenSync />
			<OrgGuard>
				<FeatureFlagProvider>
					<AppShell />
				</FeatureFlagProvider>
			</OrgGuard>
		</>
	);
}
