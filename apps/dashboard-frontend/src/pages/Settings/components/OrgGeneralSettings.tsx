import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { useOrganization } from "@clerk/react";
import { useEffect, useState } from "react";

export function OrgGeneralSettings() {
	const { organization, membership, isLoaded } = useOrganization();
	const isAdmin = membership?.role === "org:admin";

	const [name, setName] = useState("");
	const [slug, setSlug] = useState("");
	const [pending, setPending] = useState(false);
	const [error, setError] = useState("");
	const [success, setSuccess] = useState(false);

	useEffect(() => {
		if (organization) {
			setName(organization.name);
			setSlug(organization.slug ?? "");
		}
	}, [organization]);

	if (!isLoaded) {
		return (
			<Card>
				<CardHeader>
					<Skeleton className="h-6 w-24" />
				</CardHeader>
				<CardContent className="space-y-4">
					<Skeleton className="h-10 w-full" />
					<Skeleton className="h-10 w-full" />
				</CardContent>
			</Card>
		);
	}

	if (!organization) return null;

	async function handleSubmit(e: React.FormEvent) {
		e.preventDefault();
		setError("");
		setSuccess(false);
		setPending(true);

		try {
			await organization?.update({ name, slug });
			setSuccess(true);
			setTimeout(() => setSuccess(false), 3000);
		} catch (err: unknown) {
			setError(
				err instanceof Error ? err.message : "Failed to update organization.",
			);
		} finally {
			setPending(false);
		}
	}

	return (
		<Card>
			<CardHeader>
				<CardTitle>General</CardTitle>
			</CardHeader>
			<CardContent>
				<form onSubmit={handleSubmit} className="space-y-4">
					<div className="space-y-2">
						<label htmlFor="org-name" className="text-sm font-medium">
							Organization name
						</label>
						<Input
							id="org-name"
							required
							value={name}
							onChange={(e) => setName(e.target.value)}
							disabled={!isAdmin}
						/>
					</div>

					<div className="space-y-2">
						<label htmlFor="org-slug" className="text-sm font-medium">
							Slug
						</label>
						<Input
							id="org-slug"
							required
							value={slug}
							onChange={(e) => setSlug(e.target.value)}
							disabled={!isAdmin}
						/>
					</div>

					{error && <p className="text-sm text-destructive">{error}</p>}
					{success && <p className="text-sm text-primary">Saved.</p>}

					{isAdmin && (
						<Button type="submit" disabled={pending}>
							{pending ? "Saving..." : "Save Changes"}
						</Button>
					)}
				</form>
			</CardContent>
		</Card>
	);
}
