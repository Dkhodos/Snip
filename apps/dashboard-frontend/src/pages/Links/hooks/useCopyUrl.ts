import { useState } from "react";
import { getRedirectUrl } from "../helpers";

interface UseCopyUrlResult {
	copied: boolean;
	copy: (shortCode: string) => void;
}

export function useCopyUrl(): UseCopyUrlResult {
	const [copied, setCopied] = useState(false);

	function copy(shortCode: string) {
		navigator.clipboard.writeText(getRedirectUrl(shortCode));
		setCopied(true);
		setTimeout(() => setCopied(false), 2000);
	}

	return { copied, copy };
}
