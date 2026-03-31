import { useQuery } from "@tanstack/react-query";
import { type ReactNode, createContext, useContext } from "react";
import { type FeatureFlags, flagsApi } from "./api";

const FeatureFlagContext = createContext<FeatureFlags>({});

export function FeatureFlagProvider({ children }: { children: ReactNode }) {
	const { data: flags } = useQuery({
		queryKey: ["flags"],
		queryFn: () => flagsApi.getAll(),
		staleTime: 60_000,
		refetchInterval: 60_000,
	});

	return (
		<FeatureFlagContext.Provider value={flags ?? {}}>
			{children}
		</FeatureFlagContext.Provider>
	);
}

export function useFeatureFlags(): FeatureFlags {
	return useContext(FeatureFlagContext);
}
