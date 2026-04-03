import { DEV_MODE } from "@/lib/dev-mode";
import { Settings } from "lucide-react";
import { OrgGeneralSettings } from "./components/OrgGeneralSettings";
import { OrgImageUpload } from "./components/OrgImageUpload";
import { OrgMembers } from "./components/OrgMembers";

export function SettingsPage() {
	return (
		<div className="h-full overflow-y-auto">
			<div className="space-y-6">
				<h1 className="text-2xl font-bold">Settings</h1>
				{DEV_MODE ? (
					<div className="rounded-lg border border-border bg-card p-12 text-center">
						<Settings className="mx-auto h-12 w-12 text-muted-foreground" />
						<p className="mt-4 text-muted-foreground">
							Organization settings require Clerk authentication.
						</p>
					</div>
				) : (
					<>
						<OrgImageUpload />
						<OrgGeneralSettings />
						<OrgMembers />
					</>
				)}
			</div>
		</div>
	);
}
