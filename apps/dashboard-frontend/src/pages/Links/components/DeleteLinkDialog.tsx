import {
	AlertDialog,
	AlertDialogAction,
	AlertDialogCancel,
	AlertDialogContent,
	AlertDialogDescription,
	AlertDialogFooter,
	AlertDialogHeader,
	AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { type Link, linksApi } from "@/lib/api";
import { useMutation, useQueryClient } from "@tanstack/react-query";

interface DeleteLinkDialogProps {
	open: boolean;
	onOpenChange: (open: boolean) => void;
	link: Link | null;
}

export function DeleteLinkDialog({
	open,
	onOpenChange,
	link,
}: DeleteLinkDialogProps) {
	const queryClient = useQueryClient();

	const deleteMutation = useMutation({
		mutationFn: (id: string) => linksApi.remove(id),
		onSuccess: () => {
			queryClient.invalidateQueries({ queryKey: ["links"] });
			queryClient.invalidateQueries({ queryKey: ["stats"] });
			onOpenChange(false);
		},
	});

	return (
		<AlertDialog open={open} onOpenChange={onOpenChange}>
			<AlertDialogContent>
				<AlertDialogHeader>
					<AlertDialogTitle>Delete link?</AlertDialogTitle>
					<AlertDialogDescription>
						This will deactivate{" "}
						<span className="font-medium text-foreground">
							{link?.title || link?.short_code}
						</span>
						. The short code will stop redirecting.
					</AlertDialogDescription>
				</AlertDialogHeader>
				<AlertDialogFooter>
					<AlertDialogCancel>Cancel</AlertDialogCancel>
					<AlertDialogAction
						className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
						onClick={() => link && deleteMutation.mutate(link.id)}
						disabled={deleteMutation.isPending}
					>
						{deleteMutation.isPending ? "Deleting..." : "Delete"}
					</AlertDialogAction>
				</AlertDialogFooter>
			</AlertDialogContent>
		</AlertDialog>
	);
}
