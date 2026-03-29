import { useClerk } from "@clerk/react";
import { Link } from "@tanstack/react-router";
import { LogOut, Menu, Settings } from "lucide-react";
import { useState } from "react";
import { DEV_MODE } from "@/lib/dev-mode";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { Sidebar } from "./sidebar";

export function Header() {
  const [sheetOpen, setSheetOpen] = useState(false);

  return (
    <header className="flex h-14 items-center gap-4 border-b border-border bg-background px-4">
      <Sheet open={sheetOpen} onOpenChange={setSheetOpen}>
        <SheetTrigger asChild>
          <Button variant="ghost" size="icon" className="lg:hidden">
            <Menu className="h-5 w-5" />
            <span className="sr-only">Toggle menu</span>
          </Button>
        </SheetTrigger>
        <SheetContent side="left" className="w-60 p-0">
          <Sidebar />
        </SheetContent>
      </Sheet>

      <div className="flex-1" />

      <UserMenu />
    </header>
  );
}

function UserMenu() {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" className="relative h-8 w-8 rounded-full">
          <Avatar>
            <AvatarFallback>{DEV_MODE ? "DU" : "U"}</AvatarFallback>
          </Avatar>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-48">
        <DropdownMenuLabel>My Account</DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuItem asChild>
          <Link to="/settings" className="flex w-full cursor-pointer items-center gap-2">
            <Settings className="h-4 w-4" />
            Settings
          </Link>
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <SignOutItem />
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

function SignOutItem() {
  if (DEV_MODE) {
    return (
      <DropdownMenuItem className="flex cursor-pointer items-center gap-2">
        <LogOut className="h-4 w-4" />
        Sign Out
      </DropdownMenuItem>
    );
  }

  return <ClerkSignOutItem />;
}

function ClerkSignOutItem() {
  const { signOut } = useClerk();

  return (
    <DropdownMenuItem
      className="flex cursor-pointer items-center gap-2"
      onSelect={() => signOut()}
    >
      <LogOut className="h-4 w-4" />
      Sign Out
    </DropdownMenuItem>
  );
}
