import { useState, useEffect } from "react";
import { supabase } from "@/integrations/supabase/client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import { CheckCircle, XCircle } from "lucide-react";

type OrderStatus = "pending" | "approved" | "rejected" | "delivered";
type DeliveryType = "express_cars" | "delivery_company";

interface OrderAddress {
  house_no: string;
  street: string;
  ward: string;
  township: string;
  city: string;
}

interface OrderItem {
  product_id: string;
  product_name: string;
  quantity: number;
  price: number;
}

interface Order {
  id: string;
  order_string: string;
  telegram_user_id: number;
  user_name: string;
  phone: string;
  address: OrderAddress;
  items: OrderItem[];
  total_cost: number;
  delivery_type: DeliveryType;
  status: OrderStatus;
  created_at: string;
}

const OrdersTab = () => {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchOrders();
  }, []);

  const fetchOrders = async () => {
    setLoading(true);
    const { data, error } = await supabase
      .from("orders")
      .select("*")
      .order("created_at", { ascending: false });

    if (error) {
      toast.error("Failed to fetch orders");
    } else {
      setOrders((data as any) || []);
    }
    setLoading(false);
  };

  const updateOrderStatus = async (orderId: string, status: OrderStatus) => {
    const { data: { user } } = await supabase.auth.getUser();
    
    const { error } = await supabase
      .from("orders")
      .update({ 
        status,
        approved_by: status === "approved" ? user?.id : null,
        approved_at: status === "approved" ? new Date().toISOString() : null
      })
      .eq("id", orderId);

    if (error) {
      toast.error("Failed to update order status");
    } else {
      toast.success(`Order ${status === "approved" ? "approved" : "rejected"}`);
      fetchOrders();
    }
  };

  const getStatusBadge = (status: OrderStatus) => {
    const variants: Record<OrderStatus, { variant: "default" | "secondary" | "destructive" | "outline", label: string }> = {
      pending: { variant: "secondary", label: "Pending" },
      approved: { variant: "default", label: "Approved" },
      rejected: { variant: "destructive", label: "Rejected" },
      delivered: { variant: "outline", label: "Delivered" },
    };
    
    const config = variants[status] || variants.pending;
    return <Badge variant={config.variant}>{config.label}</Badge>;
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
        <h2 className="text-2xl font-bold text-foreground">Orders Management</h2>
      </div>

      {orders.length === 0 ? (
        <Card className="border-border shadow-soft">
          <CardContent className="text-center py-12">
            <p className="text-muted-foreground">No orders yet.</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {orders.map((order) => (
            <Card key={order.id} className="border-border shadow-soft">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div>
                    <CardTitle className="text-lg">Order {order.order_string}</CardTitle>
                    <p className="text-sm text-muted-foreground mt-1">
                      {new Date(order.created_at).toLocaleString()}
                    </p>
                  </div>
                  {getStatusBadge(order.status)}
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <h4 className="font-semibold text-sm text-muted-foreground mb-2">Customer Info</h4>
                    <p className="text-foreground">{order.user_name}</p>
                    <p className="text-sm text-muted-foreground">{order.phone}</p>
                    <p className="text-sm text-muted-foreground">
                      Telegram ID: {order.telegram_user_id}
                    </p>
                  </div>
                  <div>
                    <h4 className="font-semibold text-sm text-muted-foreground mb-2">Delivery</h4>
                    <p className="text-sm text-foreground capitalize">
                      {order.delivery_type.replace("_", " ")}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      {order.address.house_no}, {order.address.street}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      {order.address.ward}, {order.address.township}, {order.address.city}
                    </p>
                  </div>
                </div>

                  <div>
                    <h4 className="font-semibold text-sm text-muted-foreground mb-2">Items</h4>
                    <div className="space-y-2">
                      {order.items.map((item, idx) => (
                        <div key={idx} className="flex justify-between text-sm border-b border-border pb-2">
                          <span className="text-foreground">
                            {item.product_name} x{item.quantity}
                          </span>
                          <span className="font-semibold text-foreground">
                            ${(item.price * item.quantity).toFixed(2)}
                          </span>
                        </div>
                      ))}
                    <div className="flex justify-between text-base font-bold pt-2">
                      <span className="text-foreground">Total</span>
                      <span className="text-primary">${order.total_cost.toFixed(2)}</span>
                    </div>
                  </div>
                </div>

                {order.status === "pending" && (
                  <div className="flex gap-2 pt-2">
                    <Button
                      onClick={() => updateOrderStatus(order.id, "approved")}
                      className="flex-1 bg-success hover:bg-success/90"
                    >
                      <CheckCircle className="w-4 h-4 mr-2" />
                      Approve
                    </Button>
                    <Button
                      onClick={() => updateOrderStatus(order.id, "rejected")}
                      variant="destructive"
                      className="flex-1"
                    >
                      <XCircle className="w-4 h-4 mr-2" />
                      Reject
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default OrdersTab;