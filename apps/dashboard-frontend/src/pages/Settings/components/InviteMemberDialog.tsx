import { Button } from "@/components/ui/button";
import {
	Dialog,
	DialogContent,
	DialogDescription,
	DialogFooter,
	DialogHeader,
	DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { useOrganization } from "@clerk/react";
import { useState } from "react";

interface InviteMemberDialogProps {
	open: boolean;
	onOpenChange: (open: boolean) => void;
}

export function InviteMemberDialog({
	open,
	onOpenChange,
}: InviteMemberDialogProps) {
	const { organization } = useOrganization();
	const [email, setEmail] = useState("");
	const [role, setRole] = useState<"org:admin" | "org:member">("org:member");
	const [pending, setPending] = useState(false);
	const [error, setError] = useState("");

	async function handleSubmit(e: React.FormEvent) {
		e.preventDefault();
		if (!organization) return;

		setError("");
		setPending(true);

		try {
			await organization.inviteMember({ emailAddress: email, role });
			setEmail("");
			setRole("org:member");
			onOpenChange(false);
		} catch (err: unknown) {
			setError(
				err instanceof Error ? err.message : "Failed to send invitation.",
			);
		} finally {
			setPending(false);
		}
	}

	return (
		<Dialog open={open} onOpenChange={onOpenChange}>
			<DialogContent className="sm:max-w-md">
				<DialogHeader>
					<DialogTitle>Invite member</DialogTitle>
					<DialogDescription>
						Send an invitation to join {organization?.name}.
					</DialogDescription>
				</DialogHeader>

				<form onSubmit={handleSubmit} className="space-y-4">
					<div className="space-y-2">
						<label htmlFor="invite-email" className="text-sm font-medium">
							Email address
						</label>
						<Input
							id="invite-email"
							type="email"
							required
							value={email}
							onChange={(e) => setEmail(e.target.value)}
							placeholder="colleague@company.com"
						/>
					</div>

					<div className="space-y-2">
						<label className="text-sm font-medium">Role</label>
						<div className="flex gap-2">
							<Button
								type="button"
								variant={role === "org:member" ? "default" : "outline"}
								size="sm"
								onClick={() => setRole("org:member")}
							>
								Member
							</Button>
							<Button
								type="button"
								variant={role === "org:admin" ? "default" : "outline"}
								size="sm"
								onClick={() => setRole("org:admin")}
							>
								Admin
							</Button>
						</div>
					</div>

					{error && <p className="text-sm text-destructive">{error}</p>}

					<DialogFooter>
						<Button
							type="button"
							variant="outline"
							onClick={() => onOpenChange(false)}
						>
							Cancel
						</Button>
						<Button type="submit" disabled={pending}>
							{pending ? "Sending..." : "Send Invitation"}
						</Button>
					</DialogFooter>
				</form>
			</DialogContent>
		</Dialog>
	);
}
