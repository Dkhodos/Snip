import { Button } from "@/components/ui/button";
import {
	DropdownMenu,
	DropdownMenuContent,
	DropdownMenuItem,
	DropdownMenuSeparator,
	DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Skeleton } from "@/components/ui/skeleton";
import {
	Tooltip,
	TooltipContent,
	TooltipProvider,
	TooltipTrigger,
} from "@/components/ui/tooltip";
import { useFeatureFlags } from "@/lib/feature-flags";
import { useOrganization, useOrganizationList } from "@clerk/react";
import { Check, ChevronsUpDown, Lock, Plus } from "lucide-react";
import { useState } from "react";
import { CreateOrgDialog } from "./create-org-dialog";
import { OrgAvatar } from "./org-avatar";

export function OrgSwitcher() {
	const { organization } = useOrganization();
	const { userMemberships, setActive, isLoaded } = useOrganizationList({
		userMemberships: { infinite: true },
	});
	const flags = useFeatureFlags();
	const [createOpen, setCreateOpen] = useState(false);

	if (!isLoaded || !userMemberships.data) {
		return <Skeleton className="h-10 w-full rounded-md" />;
	}

	const hasOrg = userMemberships.data.length > 0;
	const canCreateMore = !hasOrg || flags.multiple_orgs;

	function handleSwitch(orgId: string) {
		if (setActive) {
			setActive({ organization: orgId });
		}
	}

	return (
		<>
			<DropdownMenu>
				<DropdownMenuTrigger asChild>
					<Button
						variant="outline"
						className="w-full justify-between gap-2 px-3"
					>
						<span className="flex items-center gap-2 truncate">
							{organization && (
								<OrgAvatar
									name={organization.name}
									imageUrl={organization.imageUrl}
									className="h-5 w-5"
								/>
							)}
							<span className="truncate text-sm font-medium">
								{organization?.name ?? "Select organization"}
							</span>
						</span>
						<ChevronsUpDown className="h-4 w-4 shrink-0 text-muted-foreground" />
					</Button>
				</DropdownMenuTrigger>
				<DropdownMenuContent align="start" className="w-56">
					{userMemberships.data.map((mem) => {
						const org = mem.organization;
						const isActive = org.id === organization?.id;
						return (
							<DropdownMenuItem
								key={org.id}
								onClick={() => handleSwitch(org.id)}
								className="gap-2"
							>
								<OrgAvatar
									name={org.name}
									imageUrl={org.imageUrl}
									className="h-5 w-5"
								/>
								<span className="flex-1 truncate">{org.name}</span>
								{isActive && <Check className="h-4 w-4 text-primary" />}
							</DropdownMenuItem>
						);
					})}
					<DropdownMenuSeparator />
					{canCreateMore ? (
						<DropdownMenuItem
							onClick={() => setCreateOpen(true)}
							className="gap-2"
						>
							<Plus className="h-4 w-4" />
							Create organization
						</DropdownMenuItem>
					) : (
						<TooltipProvider>
							<Tooltip>
								<TooltipTrigger asChild>
									<div className="relative flex cursor-default select-none items-center gap-2 rounded-sm px-2 py-1.5 text-sm opacity-50">
										<Lock className="h-4 w-4" />
										Create organization
									</div>
								</TooltipTrigger>
								<TooltipContent side="right" className="max-w-52">
									<p className="font-semibold">Premium Feature</p>
									<p className="text-xs text-muted-foreground">
										Creating multiple organizations requires a premium plan.
									</p>
								</TooltipContent>
							</Tooltip>
						</TooltipProvider>
					)}
				</DropdownMenuContent>
			</DropdownMenu>

			<CreateOrgDialog open={createOpen} onOpenChange={setCreateOpen} />
		</>
	);
}
