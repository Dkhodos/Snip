import { OrgSwitcher } from "@/components/org/org-switcher";
import { SnipLogo } from "@/components/snip-logo";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { DEV_MODE } from "@/lib/dev-mode";
import { cn } from "@/lib/utils";
import { Link } from "@tanstack/react-router";
import { LayoutDashboard, Link2, Settings } from "lucide-react";

interface NavItem {
	label: string;
	to: string;
	icon: React.ComponentType<{ className?: string }>;
}

const navItems: NavItem[] = [
	{ label: "Dashboard", to: "/dashboard", icon: LayoutDashboard },
	{ label: "Links", to: "/links", icon: Link2 },
	{ label: "Settings", to: "/settings", icon: Settings },
];

function NavLinks({ items }: { items: NavItem[] }) {
	return (
		<nav className="flex flex-col gap-1">
			{items.map((item) => (
				<Link
					key={item.to}
					to={item.to}
					className={cn(
						"flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground",
					)}
					activeProps={{
						className: "bg-accent text-accent-foreground",
					}}
				>
					<item.icon className="h-4 w-4" />
					{item.label}
				</Link>
			))}
		</nav>
	);
}

export function Sidebar() {
	return (
		<div className="flex h-full w-60 flex-col border-r border-border bg-background">
			<div className="flex h-14 items-center gap-2 px-4">
				<SnipLogo size={28} className="text-primary" />
				<span className="text-lg font-semibold tracking-tight">Snip</span>
			</div>

			<Separator />

			<div className="px-3 py-3">
				{DEV_MODE ? (
					<div className="flex items-center gap-2 rounded-md border border-border px-3 py-2">
						<span className="text-sm font-medium">Dev Org</span>
					</div>
				) : (
					<OrgSwitcher />
				)}
			</div>

			<Separator />

			<ScrollArea className="flex-1 px-3 py-4">
				<NavLinks items={navItems} />
			</ScrollArea>
		</div>
	);
}
