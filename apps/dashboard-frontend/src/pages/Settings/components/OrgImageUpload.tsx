import { OrgAvatar } from "@/components/org/org-avatar";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useOrganization } from "@clerk/react";
import { Camera, Trash2 } from "lucide-react";
import { useRef, useState } from "react";

export const ACCEPTED_TYPES = [
	"image/jpeg",
	"image/png",
	"image/gif",
	"image/webp",
];
export const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10 MB

export function validateFile(file: File): string | null {
	if (!ACCEPTED_TYPES.includes(file.type)) {
		return "Please upload a JPEG, PNG, GIF, or WebP image.";
	}
	if (file.size > MAX_FILE_SIZE) {
		return "Image must be under 10 MB.";
	}
	return null;
}

export function OrgImageUpload() {
	const { organization, membership, isLoaded } = useOrganization();
	const isAdmin = membership?.role === "org:admin";
	const fileInputRef = useRef<HTMLInputElement>(null);

	const [uploading, setUploading] = useState(false);
	const [error, setError] = useState("");
	const [success, setSuccess] = useState(false);

	if (!isLoaded) {
		return (
			<Card>
				<CardHeader>
					<Skeleton className="h-6 w-40" />
				</CardHeader>
				<CardContent>
					<Skeleton className="h-20 w-20 rounded-full" />
				</CardContent>
			</Card>
		);
	}

	if (!organization) return null;

	const hasImage = organization.hasImage;

	async function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
		const file = e.target.files?.[0];
		if (!file || !organization) return;

		const validationError = validateFile(file);
		if (validationError) {
			setError(validationError);
			return;
		}

		setError("");
		setSuccess(false);
		setUploading(true);

		try {
			await organization.setLogo({ file });
			setSuccess(true);
			setTimeout(() => setSuccess(false), 3000);
		} catch (err: unknown) {
			setError(err instanceof Error ? err.message : "Failed to upload image.");
		} finally {
			setUploading(false);
			if (fileInputRef.current) {
				fileInputRef.current.value = "";
			}
		}
	}

	async function handleRemove() {
		if (!organization) return;

		setError("");
		setSuccess(false);
		setUploading(true);

		try {
			await organization.setLogo({ file: null });
			setSuccess(true);
			setTimeout(() => setSuccess(false), 3000);
		} catch (err: unknown) {
			setError(err instanceof Error ? err.message : "Failed to remove image.");
		} finally {
			setUploading(false);
		}
	}

	return (
		<Card>
			<CardHeader>
				<CardTitle>Organization image</CardTitle>
			</CardHeader>
			<CardContent className="flex items-center gap-6">
				<OrgAvatar
					name={organization.name}
					imageUrl={organization.imageUrl}
					className="h-20 w-20 text-xl"
				/>

				{isAdmin && (
					<div className="space-y-3">
						<div className="flex items-center gap-2">
							<Button
								type="button"
								variant="outline"
								size="sm"
								disabled={uploading}
								onClick={() => fileInputRef.current?.click()}
							>
								<Camera className="mr-2 h-4 w-4" />
								{uploading ? "Uploading..." : "Upload image"}
							</Button>

							{hasImage && (
								<Button
									type="button"
									variant="ghost"
									size="sm"
									disabled={uploading}
									onClick={handleRemove}
								>
									<Trash2 className="mr-2 h-4 w-4" />
									Remove
								</Button>
							)}
						</div>

						<p className="text-xs text-muted-foreground">
							JPEG, PNG, GIF, or WebP. Max 10 MB.
						</p>

						{error && <p className="text-sm text-destructive">{error}</p>}
						{success && <p className="text-sm text-primary">Updated.</p>}

						<input
							ref={fileInputRef}
							type="file"
							accept={ACCEPTED_TYPES.join(",")}
							className="hidden"
							onChange={handleFileChange}
						/>
					</div>
				)}
			</CardContent>
		</Card>
	);
}
