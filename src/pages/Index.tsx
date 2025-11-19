import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Package, ShoppingCart, Users, MessageSquare, ArrowRight } from "lucide-react";

const Index = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-secondary to-background">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center max-w-3xl mx-auto space-y-8">
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-gradient-primary shadow-medium mb-4">
            <Package className="w-10 h-10 text-primary-foreground" />
          </div>
          
          <h1 className="text-5xl font-bold text-foreground">
            Telegram Order Bot
          </h1>
          
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Professional order management system for your Telegram bot. Manage products, process orders, and engage with customers.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center pt-4">
            <Button asChild size="lg" className="bg-gradient-primary shadow-soft text-lg">
              <Link to="/auth">
                Get Started
                <ArrowRight className="ml-2 w-5 h-5" />
              </Link>
            </Button>
            <Button asChild size="lg" variant="outline">
              <Link to="/auth">Admin Login</Link>
            </Button>
          </div>

          <div className="grid md:grid-cols-4 gap-6 pt-12">
            <div className="p-6 rounded-xl bg-card border border-border shadow-soft">
              <Package className="w-8 h-8 text-primary mb-3" />
              <h3 className="font-semibold text-foreground mb-2">Products</h3>
              <p className="text-sm text-muted-foreground">Manage inventory with ease</p>
            </div>
            <div className="p-6 rounded-xl bg-card border border-border shadow-soft">
              <ShoppingCart className="w-8 h-8 text-primary mb-3" />
              <h3 className="font-semibold text-foreground mb-2">Orders</h3>
              <p className="text-sm text-muted-foreground">Track and approve orders</p>
            </div>
            <div className="p-6 rounded-xl bg-card border border-border shadow-soft">
              <Users className="w-8 h-8 text-primary mb-3" />
              <h3 className="font-semibold text-foreground mb-2">Users</h3>
              <p className="text-sm text-muted-foreground">Manage customer accounts</p>
            </div>
            <div className="p-6 rounded-xl bg-card border border-border shadow-soft">
              <MessageSquare className="w-8 h-8 text-primary mb-3" />
              <h3 className="font-semibold text-foreground mb-2">Broadcast</h3>
              <p className="text-sm text-muted-foreground">Reach all customers instantly</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Index;
