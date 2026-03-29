import { useOrganizationList } from "@clerk/react";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

interface CreateOrgFormProps {
  onSuccess?: () => void;
}

function slugify(value: string): string {
  return value
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, "")
    .replace(/\s+/g, "-")
    .replace(/-+/g, "-")
    .replace(/^-|-$/g, "");
}

export function CreateOrgForm({ onSuccess }: CreateOrgFormProps) {
  const { createOrganization, setActive } = useOrganizationList();
  const [name, setName] = useState("");
  const [slug, setSlug] = useState("");
  const [slugTouched, setSlugTouched] = useState(false);
  const [error, setError] = useState("");
  const [pending, setPending] = useState(false);

  function handleNameChange(value: string) {
    setName(value);
    if (!slugTouched) {
      setSlug(slugify(value));
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!createOrganization || !setActive) return;

    setError("");
    setPending(true);

    try {
      const org = await createOrganization({ name, slug });
      await setActive({ organization: org.id });
      onSuccess?.();
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Failed to create organization. The slug may already be taken.");
      }
    } finally {
      setPending(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="space-y-2">
        <label htmlFor="org-name" className="text-sm font-medium">
          Organization name
        </label>
        <Input
          id="org-name"
          required
          value={name}
          onChange={(e) => handleNameChange(e.target.value)}
          placeholder="Acme Corp"
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
          onChange={(e) => {
            setSlugTouched(true);
            setSlug(slugify(e.target.value));
          }}
          placeholder="acme-corp"
        />
        <p className="text-xs text-muted-foreground">
          Unique identifier. Lowercase letters, numbers, and hyphens only.
        </p>
      </div>

      {error && (
        <p className="text-sm text-destructive">{error}</p>
      )}

      <Button type="submit" className="w-full" disabled={pending}>
        {pending ? "Creating..." : "Create Organization"}
      </Button>
    </form>
  );
}
