import { setAuthToken } from "@/lib/api";
import { useAuth, useOrganization } from "@clerk/react";
import { useQueryClient } from "@tanstack/react-query";
import { type ReactNode, useEffect, useRef, useState } from "react";

interface AuthTokenSyncProps {
	children: ReactNode;
	fallback?: ReactNode;
}

export function AuthTokenSync({
	children,
	fallback = null,
}: AuthTokenSyncProps) {
	const { getToken } = useAuth();
	const { organization } = useOrganization();
	const queryClient = useQueryClient();
	const prevOrgId = useRef<string | null>(null);
	const [ready, setReady] = useState(false);

	const orgId = organization?.id ?? null;

	useEffect(() => {
		let mounted = true;

		async function sync() {
			const token = await getToken({ skipCache: true });
			if (mounted) {
				setAuthToken(token);
				setReady(true);
			}
		}

		sync();

		// Invalidate all queries when org changes (not on initial mount)
		if (prevOrgId.current !== null && prevOrgId.current !== orgId) {
			queryClient.invalidateQueries();
		}
		prevOrgId.current = orgId;

		// Re-sync every 50s (Clerk tokens expire ~60s)
		const interval = setInterval(sync, 50_000);
		return () => {
			mounted = false;
			clearInterval(interval);
		};
	}, [getToken, orgId, queryClient]);

	if (!ready) {
		return <>{fallback}</>;
	}

	return <>{children}</>;
}
