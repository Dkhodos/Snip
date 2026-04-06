import { Button } from "@/components/ui/button";
import {
	DropdownMenu,
	DropdownMenuContent,
	DropdownMenuItem,
	DropdownMenuSeparator,
	DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import type { Link } from "@/lib/api";
import {
	Copy,
	ExternalLink,
	Image,
	MoreHorizontal,
	Pencil,
	Trash2,
} from "lucide-react";
import { getRedirectUrl } from "../helpers";

interface LinkRowActionsProps {
	link: Link;
	onEdit: (link: Link) => void;
	onDelete: (link: Link) => void;
	onPreview: (link: Link) => void;
	onCopy: (shortCode: string) => void;
}

export function LinkRowActions({
	link,
	onEdit,
	onDelete,
	onPreview,
	onCopy,
}: LinkRowActionsProps) {
	return (
		<DropdownMenu>
			<DropdownMenuTrigger asChild>
				<Button variant="ghost" size="icon" className="h-8 w-8">
					<MoreHorizontal className="h-4 w-4" />
				</Button>
			</DropdownMenuTrigger>
			<DropdownMenuContent align="end">
				<DropdownMenuItem onClick={() => onCopy(link.short_code)}>
					<Copy className="mr-2 h-4 w-4" />
					Copy URL
				</DropdownMenuItem>
				<DropdownMenuItem asChild>
					<a
						href={getRedirectUrl(link.short_code)}
						target="_blank"
						rel="noopener noreferrer"
					>
						<ExternalLink className="mr-2 h-4 w-4" />
						Open in new tab
					</a>
				</DropdownMenuItem>
				<DropdownMenuItem onClick={() => onPreview(link)}>
					<Image className="mr-2 h-4 w-4" />
					Preview OG Image
				</DropdownMenuItem>
				<DropdownMenuItem onClick={() => onEdit(link)}>
					<Pencil className="mr-2 h-4 w-4" />
					Edit
				</DropdownMenuItem>
				<DropdownMenuSeparator />
				<DropdownMenuItem
					className="text-destructive"
					onClick={() => onDelete(link)}
				>
					<Trash2 className="mr-2 h-4 w-4" />
					Delete
				</DropdownMenuItem>
			</DropdownMenuContent>
		</DropdownMenu>
	);
}
