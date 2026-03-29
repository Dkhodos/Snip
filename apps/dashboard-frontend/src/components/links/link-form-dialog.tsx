import { useState, useEffect } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  createLink,
  updateLink,
  type Link,
  type CreateLinkRequest,
  type UpdateLinkRequest,
} from "@/lib/api";

interface LinkFormDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  link?: Link | null;
}

export function LinkFormDialog({ open, onOpenChange, link }: LinkFormDialogProps) {
  const isEditing = !!link;
  const queryClient = useQueryClient();

  const [targetUrl, setTargetUrl] = useState("");
  const [title, setTitle] = useState("");
  const [customCode, setCustomCode] = useState("");

  useEffect(() => {
    if (open) {
      setTargetUrl(link?.target_url ?? "");
      setTitle(link?.title ?? "");
      setCustomCode("");
    }
  }, [open, link]);

  const createMutation = useMutation({
    mutationFn: (body: CreateLinkRequest) => createLink(body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["links"] });
      queryClient.invalidateQueries({ queryKey: ["stats"] });
      onOpenChange(false);
    },
  });

  const updateMutation = useMutation({
    mutationFn: (body: UpdateLinkRequest) => updateLink(link!.id, body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["links"] });
      onOpenChange(false);
    },
  });

  const isPending = createMutation.isPending || updateMutation.isPending;
  const error = createMutation.error || updateMutation.error;

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (isEditing) {
      const updates: UpdateLinkRequest = {};
      if (targetUrl !== link!.target_url) updates.target_url = targetUrl;
      if (title !== (link!.title ?? "")) updates.title = title;
      updateMutation.mutate(updates);
    } else {
      createMutation.mutate({
        target_url: targetUrl,
        title,
        custom_short_code: customCode || undefined,
      });
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{isEditing ? "Edit Link" : "Create Link"}</DialogTitle>
          <DialogDescription>
            {isEditing
              ? "Update the link details below."
              : "Add a new shortened link."}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <label htmlFor="title" className="text-sm font-medium">
              Title
            </label>
            <Input
              id="title"
              type="text"
              required
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="My awesome link"
            />
          </div>

          <div className="space-y-2">
            <label htmlFor="target_url" className="text-sm font-medium">
              Target URL
            </label>
            <Input
              id="target_url"
              type="url"
              required
              value={targetUrl}
              onChange={(e) => setTargetUrl(e.target.value)}
              placeholder="https://example.com"
            />
          </div>

          {!isEditing && (
            <div className="space-y-2">
              <label htmlFor="custom_code" className="text-sm font-medium">
                Custom Short Code{" "}
                <span className="text-muted-foreground">(optional)</span>
              </label>
              <Input
                id="custom_code"
                type="text"
                value={customCode}
                onChange={(e) => setCustomCode(e.target.value)}
                placeholder="my-link"
              />
              <p className="text-xs text-muted-foreground">
                Leave blank to auto-generate. Must be unique.
              </p>
            </div>
          )}

          {error && (
            <p className="text-sm text-destructive">
              {isEditing ? "Failed to update link." : "Failed to create link."}{" "}
              Please try again.
            </p>
          )}

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={isPending}>
              {isPending
                ? isEditing
                  ? "Saving..."
                  : "Creating..."
                : isEditing
                  ? "Save Changes"
                  : "Create Link"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
