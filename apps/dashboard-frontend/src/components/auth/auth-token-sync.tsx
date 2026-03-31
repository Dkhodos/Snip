import { setAuthToken } from "@/lib/api";
import { useAuth, useOrganization } from "@clerk/react";
import { useQueryClient } from "@tanstack/react-query";
import { useEffect, useRef } from "react";

export function AuthTokenSync() {
	const { getToken } = useAuth();
	const { organization } = useOrganization();
	const queryClient = useQueryClient();
	const prevOrgId = useRef<string | null>(null);

	const orgId = organization?.id ?? null;

	useEffect(() => {
		let mounted = true;

		async function sync() {
			const token = await getToken({ skipCache: true });
			if (mounted) {
				setAuthToken(token);
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

	return null;
}
