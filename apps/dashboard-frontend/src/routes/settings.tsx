import { SettingsPage } from "@/pages/Settings/SettingsPage";
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/settings")({
	component: SettingsPage,
});
