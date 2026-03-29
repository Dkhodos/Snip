import { useQuery } from "@tanstack/react-query";
import { createContext, useContext, type ReactNode } from "react";
import { type FeatureFlags, fetchFlags } from "./api";

const FeatureFlagContext = createContext<FeatureFlags>({});

export function FeatureFlagProvider({ children }: { children: ReactNode }) {
  const { data: flags } = useQuery({
    queryKey: ["flags"],
    queryFn: fetchFlags,
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
