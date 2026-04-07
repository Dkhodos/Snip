import { Button } from "@/components/ui/button";
import {
	Dialog,
	DialogContent,
	DialogDescription,
	DialogFooter,
	DialogHeader,
	DialogTitle,
} from "@/components/ui/dialog";
import type { Link } from "@/lib/api";
import { linksApi } from "@/lib/api";
import { cn } from "@/lib/utils";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Copy, RefreshCw } from "lucide-react";
import { useState } from "react";
import { OgImagePreview } from "./OgImagePreview";

interface OgPreviewDialogProps {
	open: boolean;
	onOpenChange: (open: boolean) => void;
	link: Link | null;
}

export function OgPreviewDialog({
	open,
	onOpenChange,
	link,
}: OgPreviewDialogProps) {
	const [imgLoaded, setImgLoaded] = useState(false);
	const [imgFailed, setImgFailed] = useState(false);
	const [copied, setCopied] = useState(false);
	const [cacheBust, setCacheBust] = useState<string>("");

	const urlQuery = useQuery({
		queryKey: ["og-image-url", link?.id],
		// biome-ignore lint/style/noNonNullAssertion: enabled only when link is defined
		queryFn: () => linksApi.getOgImageUrl(link!.id),
		enabled: open && !!link,
		staleTime: Number.POSITIVE_INFINITY,
	});

	const generateMutation = useMutation({
		mutationFn: (id: string) => linksApi.generateOgImage(id),
		onSuccess: () => {
			setImgLoaded(false);
			setImgFailed(false);
			setCacheBust(`?t=${Date.now()}`);
		},
	});

	const handleOpenChange = (next: boolean) => {
		if (!next) {
			setImgLoaded(false);
			setImgFailed(false);
			setCacheBust("");
		}
		onOpenChange(next);
	};

	function handleRegenerate() {
		if (link) {
			setImgLoaded(false);
			setImgFailed(false);
			setCacheBust("");
			generateMutation.mutate(link.id);
		}
	}

	function handleCopyUrl() {
		const url = urlQuery.data?.og_image_url;
		if (url) {
			navigator.clipboard.writeText(url);
			setCopied(true);
			setTimeout(() => setCopied(false), 2000);
		}
	}

	function handleImageError() {
		setImgFailed(true);
		if (link && !generateMutation.isPending) {
			generateMutation.mutate(link.id);
		}
	}

	const isGenerating = generateMutation.isPending;
	const isGenerateError = generateMutation.isError && imgFailed;
	const imgSrc = urlQuery.data?.og_image_url
		? `${urlQuery.data.og_image_url}${cacheBust}`
		: null;

	return (
		<Dialog open={open} onOpenChange={handleOpenChange}>
			<DialogContent className="max-w-2xl">
				<DialogHeader>
					<DialogTitle>OG Image Preview</DialogTitle>
					<DialogDescription>
						This image is shown when{" "}
						<span className="font-medium text-foreground">
							{link?.title || link?.short_code}
						</span>{" "}
						is shared on Slack, LinkedIn, or Twitter.
					</DialogDescription>
				</DialogHeader>

				<OgImagePreview
					imgSrc={imgSrc}
					imgLoaded={imgLoaded}
					isGenerating={isGenerating}
					isError={isGenerateError}
					onLoad={() => setImgLoaded(true)}
					onError={handleImageError}
				/>

				<DialogFooter className="flex-row gap-2 sm:justify-between">
					<div className="flex gap-2">
						<Button
							variant="outline"
							size="sm"
							onClick={handleRegenerate}
							disabled={isGenerating}
						>
							<RefreshCw
								className={cn(
									"mr-2 h-3.5 w-3.5",
									isGenerating && "animate-spin",
								)}
							/>
							{isGenerating ? "Generating…" : "Regenerate"}
						</Button>
						<Button variant="outline" size="sm" onClick={handleCopyUrl}>
							<Copy className="mr-2 h-3.5 w-3.5" />
							{copied ? "Copied!" : "Copy URL"}
						</Button>
					</div>
					<Button
						variant="ghost"
						size="sm"
						onClick={() => handleOpenChange(false)}
					>
						Close
					</Button>
				</DialogFooter>
			</DialogContent>
		</Dialog>
	);
}
