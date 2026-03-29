import { useOrganization } from "@clerk/react";
import { UserPlus, Trash2, Mail, Clock } from "lucide-react";
import { useState } from "react";
import {
  AlertDialog,
  AlertDialogContent,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogCancel,
  AlertDialogAction,
} from "@/components/ui/alert-dialog";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { InviteMemberDialog } from "./invite-member-dialog";

export function OrgMembers() {
  const { organization, membership, memberships, invitations, isLoaded } = useOrganization({
    memberships: { infinite: true },
    invitations: { infinite: true },
  });
  const isAdmin = membership?.role === "org:admin";
  const [inviteOpen, setInviteOpen] = useState(false);
  const [removingUserId, setRemovingUserId] = useState<string | null>(null);
  const [removingName, setRemovingName] = useState("");

  if (!isLoaded) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-24" />
        </CardHeader>
        <CardContent className="space-y-2">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-12 w-full" />
          ))}
        </CardContent>
      </Card>
    );
  }

  if (!organization) return null;

  async function handleRemove() {
    if (!removingUserId) return;
    try {
      await organization!.removeMember(removingUserId);
    } catch {
      // Clerk will throw if user can't be removed
    } finally {
      setRemovingUserId(null);
    }
  }

  const pendingInvitations = invitations?.data?.filter((inv) => inv.status === "pending") ?? [];

  return (
    <>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0">
          <CardTitle>Members</CardTitle>
          {isAdmin && (
            <Button size="sm" onClick={() => setInviteOpen(true)}>
              <UserPlus className="mr-2 h-4 w-4" />
              Invite
            </Button>
          )}
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>User</TableHead>
                  <TableHead>Role</TableHead>
                  {isAdmin && <TableHead className="w-[50px]" />}
                </TableRow>
              </TableHeader>
              <TableBody>
                {memberships?.data?.map((mem) => {
                  const user = mem.publicUserData;
                  const name = [user?.firstName, user?.lastName].filter(Boolean).join(" ") || "Unknown";
                  const initials = name.split(/\s+/).map((w) => w[0]).join("").toUpperCase().slice(0, 2);

                  return (
                    <TableRow key={mem.id}>
                      <TableCell>
                        <div className="flex items-center gap-3">
                          <Avatar className="h-8 w-8">
                            {user?.imageUrl && <AvatarImage src={user.imageUrl} alt={name} />}
                            <AvatarFallback className="text-xs">{initials}</AvatarFallback>
                          </Avatar>
                          <div>
                            <p className="text-sm font-medium">{name}</p>
                            <p className="text-xs text-muted-foreground">{user?.identifier}</p>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge variant={mem.role === "org:admin" ? "default" : "secondary"}>
                          {mem.role === "org:admin" ? "Admin" : "Member"}
                        </Badge>
                      </TableCell>
                      {isAdmin && (
                        <TableCell>
                          {mem.publicUserData?.userId !== membership?.publicUserData?.userId && (
                            <Button
                              variant="ghost"
                              size="icon"
                              className="h-8 w-8 text-destructive hover:text-destructive"
                              onClick={() => {
                                setRemovingUserId(mem.publicUserData?.userId ?? null);
                                setRemovingName(name);
                              }}
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          )}
                        </TableCell>
                      )}
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </div>

          {pendingInvitations.length > 0 && (
            <div className="space-y-3">
              <h3 className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
                <Clock className="h-4 w-4" />
                Pending Invitations
              </h3>
              <div className="rounded-md border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Email</TableHead>
                      <TableHead>Role</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {pendingInvitations.map((inv) => (
                      <TableRow key={inv.id}>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            <Mail className="h-4 w-4 text-muted-foreground" />
                            <span className="text-sm">{inv.emailAddress}</span>
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge variant="secondary">
                            {inv.role === "org:admin" ? "Admin" : "Member"}
                          </Badge>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      <InviteMemberDialog open={inviteOpen} onOpenChange={setInviteOpen} />

      <AlertDialog open={!!removingUserId} onOpenChange={(open) => { if (!open) setRemovingUserId(null); }}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Remove member?</AlertDialogTitle>
            <AlertDialogDescription>
              <span className="font-medium text-foreground">{removingName}</span>{" "}
              will lose access to this organization.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
              onClick={handleRemove}
            >
              Remove
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}
