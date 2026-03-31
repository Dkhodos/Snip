import { DashboardPage } from "@/pages/Dashboard/DashboardPage";
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/dashboard")({
	component: DashboardPage,
});
