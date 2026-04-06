import { cn } from "@/lib/utils";
import { RefreshCw } from "lucide-react";

interface OgImagePreviewProps {
	imgSrc: string | null;
	imgLoaded: boolean;
	isGenerating: boolean;
	isError: boolean;
	onLoad: () => void;
	onError: () => void;
}

export function OgImagePreview({
	imgSrc,
	imgLoaded,
	isGenerating,
	isError,
	onLoad,
	onError,
}: OgImagePreviewProps) {
	return (
		<div className="relative w-full overflow-hidden rounded-lg border bg-muted aspect-[1200/630]">
			{/* Skeleton: always present until image fades in */}
			<div
				className={cn(
					"absolute inset-0 transition-opacity duration-300",
					!imgLoaded && !isError
						? "opacity-100"
						: "opacity-0 pointer-events-none",
				)}
			>
				{isGenerating ? (
					<div className="flex h-full flex-col items-center justify-center gap-3">
						<RefreshCw className="h-6 w-6 animate-spin text-muted-foreground" />
						<span className="text-sm text-muted-foreground">Generating…</span>
					</div>
				) : (
					<div className="h-full w-full animate-pulse bg-muted-foreground/10" />
				)}
			</div>

			{/* Error state */}
			{isError && (
				<div className="absolute inset-0 flex items-center justify-center text-sm text-muted-foreground">
					Failed to generate image. Try regenerating.
				</div>
			)}

			{/* Image: starts invisible, fades in on load */}
			{imgSrc && !isError && (
				<img
					key={imgSrc}
					src={imgSrc}
					alt="OG preview"
					className={cn(
						"absolute inset-0 h-full w-full object-cover rounded-lg",
						"transition-opacity duration-500",
						imgLoaded ? "opacity-100" : "opacity-0",
					)}
					onLoad={onLoad}
					onError={onError}
				/>
			)}
		</div>
	);
}
