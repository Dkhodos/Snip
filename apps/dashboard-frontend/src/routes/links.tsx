import { LinksPage } from "@/pages/Links/LinksPage";
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/links")({
	component: LinksPage,
});
