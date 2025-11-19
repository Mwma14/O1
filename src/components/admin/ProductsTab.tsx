import { useState, useEffect } from "react";
import { supabase } from "@/integrations/supabase/client";
import { Button } from "@/components/ui/button";
import { Plus, Edit, Trash2, Link as LinkIcon } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { toast } from "sonner";
import ProductDialog from "./ProductDialog";
import { Badge } from "@/components/ui/badge";

interface Product {
  id: string;
  product_id: string;
  name: string;
  description: string | null;
  price: number;
  stock: number;
  image_url: string | null;
  is_active: boolean;
}

const ProductsTab = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingProduct, setEditingProduct] = useState<Product | null>(null);

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    setLoading(true);
    const { data, error } = await supabase
      .from("products")
      .select("*")
      .order("created_at", { ascending: false });

    if (error) {
      toast.error("Failed to fetch products");
    } else {
      setProducts(data || []);
    }
    setLoading(false);
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to delete this product?")) return;

    const { error } = await supabase
      .from("products")
      .delete()
      .eq("id", id);

    if (error) {
      toast.error("Failed to delete product");
    } else {
      toast.success("Product deleted successfully");
      fetchProducts();
    }
  };

  const copyDeepLink = (productId: string) => {
    const link = `https://t.me/YOUR_BOT_USERNAME?start=${productId}`;
    navigator.clipboard.writeText(link);
    toast.success("Deep link copied to clipboard!");
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-foreground">Products Management</h2>
        <Button onClick={() => { setEditingProduct(null); setDialogOpen(true); }} className="bg-gradient-primary shadow-soft">
          <Plus className="w-4 h-4 mr-2" />
          Add Product
        </Button>
      </div>

      {loading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
        </div>
      ) : products.length === 0 ? (
        <Card className="border-border shadow-soft">
          <CardContent className="text-center py-12">
            <p className="text-muted-foreground">No products yet. Create your first product!</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {products.map((product) => (
            <Card key={product.id} className="border-border shadow-soft hover:shadow-medium transition-shadow">
              <CardContent className="p-6">
                {product.image_url && (
                  <img src={product.image_url} alt={product.name} className="w-full h-40 object-cover rounded-lg mb-4" />
                )}
                <div className="space-y-3">
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="font-semibold text-foreground">{product.name}</h3>
                      <p className="text-sm text-muted-foreground">ID: {product.product_id}</p>
                    </div>
                    {!product.is_active && (
                      <Badge variant="secondary">Inactive</Badge>
                    )}
                  </div>
                  <p className="text-sm text-muted-foreground line-clamp-2">{product.description}</p>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-lg font-bold text-foreground">${product.price}</p>
                      <p className="text-sm text-muted-foreground">Stock: {product.stock}</p>
                    </div>
                  </div>
                  <div className="flex gap-2 pt-2">
                    <Button variant="outline" size="sm" onClick={() => copyDeepLink(product.product_id)} className="flex-1">
                      <LinkIcon className="w-3 h-3 mr-1" />
                      Copy Link
                    </Button>
                    <Button variant="outline" size="sm" onClick={() => { setEditingProduct(product); setDialogOpen(true); }}>
                      <Edit className="w-3 h-3" />
                    </Button>
                    <Button variant="outline" size="sm" onClick={() => handleDelete(product.id)}>
                      <Trash2 className="w-3 h-3" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <ProductDialog
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        product={editingProduct}
        onSuccess={fetchProducts}
      />
    </div>
  );
};

export default ProductsTab;