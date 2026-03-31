import { DevToolsPage } from "@/pages/Dev/DevToolsPage";
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/dev")({
	component: DevToolsPage,
});
