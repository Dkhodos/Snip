import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { cn } from "@/lib/utils";

interface OrgAvatarProps {
  name: string;
  imageUrl?: string | null;
  className?: string;
}

export function OrgAvatar({ name, imageUrl, className }: OrgAvatarProps) {
  const initials = name
    .split(/\s+/)
    .map((w) => w[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);

  return (
    <Avatar className={cn("h-8 w-8", className)}>
      {imageUrl && <AvatarImage src={imageUrl} alt={name} />}
      <AvatarFallback className="bg-primary/10 text-xs font-medium text-primary">
        {initials}
      </AvatarFallback>
    </Avatar>
  );
}
