import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { CreateOrgForm } from "./create-org-form";

interface CreateOrgDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function CreateOrgDialog({ open, onOpenChange }: CreateOrgDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Create organization</DialogTitle>
          <DialogDescription>
            Choose a name and unique slug for your new team.
          </DialogDescription>
        </DialogHeader>
        <CreateOrgForm onSuccess={() => onOpenChange(false)} />
      </DialogContent>
    </Dialog>
  );
}
