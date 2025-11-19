import { useState, useEffect } from "react";
import { supabase } from "@/integrations/supabase/client";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import { Ban, ShieldCheck } from "lucide-react";

interface Profile {
  id: string;
  telegram_user_id: number | null;
  username: string | null;
  phone: string | null;
  is_banned: boolean;
  created_at: string;
}

const UsersTab = () => {
  const [users, setUsers] = useState<Profile[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    setLoading(true);
    const { data, error } = await supabase
      .from("profiles")
      .select("*")
      .order("created_at", { ascending: false });

    if (error) {
      toast.error("Failed to fetch users");
    } else {
      setUsers(data || []);
    }
    setLoading(false);
  };

  const toggleBan = async (userId: string, currentBanStatus: boolean) => {
    const { error } = await supabase
      .from("profiles")
      .update({ is_banned: !currentBanStatus })
      .eq("id", userId);

    if (error) {
      toast.error("Failed to update user status");
    } else {
      toast.success(currentBanStatus ? "User unbanned" : "User banned");
      fetchUsers();
    }
  };

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-foreground">User Management</h2>
      </div>

      {users.length === 0 ? (
        <Card className="border-border shadow-soft">
          <CardContent className="text-center py-12">
            <p className="text-muted-foreground">No users yet.</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {users.map((user) => (
            <Card key={user.id} className="border-border shadow-soft">
              <CardContent className="p-6 space-y-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="font-semibold text-foreground">
                      {user.username || "Unknown User"}
                    </h3>
                    {user.telegram_user_id && (
                      <p className="text-sm text-muted-foreground">
                        Telegram ID: {user.telegram_user_id}
                      </p>
                    )}
                    {user.phone && (
                      <p className="text-sm text-muted-foreground">{user.phone}</p>
                    )}
                  </div>
                  {user.is_banned ? (
                    <Badge variant="destructive">Banned</Badge>
                  ) : (
                    <Badge variant="outline">Active</Badge>
                  )}
                </div>

                <p className="text-xs text-muted-foreground">
                  Joined: {new Date(user.created_at).toLocaleDateString()}
                </p>

                <Button
                  onClick={() => toggleBan(user.id, user.is_banned)}
                  variant={user.is_banned ? "outline" : "destructive"}
                  size="sm"
                  className="w-full"
                >
                  {user.is_banned ? (
                    <>
                      <ShieldCheck className="w-4 h-4 mr-2" />
                      Unban User
                    </>
                  ) : (
                    <>
                      <Ban className="w-4 h-4 mr-2" />
                      Ban User
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default UsersTab;