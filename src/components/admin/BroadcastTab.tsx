import { useState } from "react";
import { supabase } from "@/integrations/supabase/client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { toast } from "sonner";
import { Send } from "lucide-react";

const BroadcastTab = () => {
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const handleBroadcast = async () => {
    if (!message.trim()) {
      toast.error("Please enter a message");
      return;
    }

    setLoading(true);
    
    const { data: { user } } = await supabase.auth.getUser();
    if (!user) {
      toast.error("Not authenticated");
      setLoading(false);
      return;
    }

    // Get count of active users
    const { data: profiles, error: profilesError } = await supabase
      .from("profiles")
      .select("id")
      .eq("is_banned", false);

    if (profilesError) {
      toast.error("Failed to get user count");
      setLoading(false);
      return;
    }

    // Save broadcast message
    const { error } = await supabase
      .from("broadcast_messages")
      .insert({
        message: message.trim(),
        sent_by: user.id,
        recipient_count: profiles?.length || 0
      });

    if (error) {
      toast.error("Failed to save broadcast message");
    } else {
      toast.success(`Broadcast message saved! Will be sent to ${profiles?.length || 0} users via Telegram bot.`);
      setMessage("");
    }

    setLoading(false);
  };

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold text-foreground mb-6">Broadcast Message</h2>

      <Card className="border-border shadow-soft">
        <CardHeader>
          <CardTitle>Send message to all users</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Textarea
            placeholder="Type your broadcast message here..."
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            rows={6}
            className="resize-none"
          />
          <Button
            onClick={handleBroadcast}
            disabled={loading || !message.trim()}
            className="w-full bg-gradient-primary shadow-soft"
          >
            <Send className="w-4 h-4 mr-2" />
            {loading ? "Sending..." : "Send Broadcast"}
          </Button>
          <p className="text-sm text-muted-foreground">
            This message will be saved to the database. Your Telegram bot should check for new broadcast messages and send them to all active users.
          </p>
        </CardContent>
      </Card>
    </div>
  );
};

export default BroadcastTab;