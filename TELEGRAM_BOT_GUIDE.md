# Telegram Bot Integration Guide

This document explains how to connect your Python Telegram bot to this admin panel.

## 📋 Database Connection

Your Telegram bot should connect to the same Supabase database. Use these connection details:

- **Supabase URL**: `https://dwaxejcqvtkeavngwrzk.supabase.co`
- **Supabase Anon Key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR3YXhlamNxdnRrZWF2bmd3cnprIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjM0NDY2NTIsImV4cCI6MjA3OTAyMjY1Mn0.o5kO7P4lpnQU8brNliTORSYBZPOwdt8anp9RvuCM6Uo`

Install the Supabase Python client:
```bash
pip install supabase
```

## 🔧 Bot Setup Example

```python
from supabase import create_client, Client
import os

# Initialize Supabase client
supabase: Client = create_client(
    "https://dwaxejcqvtkeavngwrzk.supabase.co",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR3YXhlamNxdnRrZWF2bmd3cnprIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjM0NDY2NTIsImV4cCI6MjA3OTAyMjY1Mn0.o5kO7P4lpnQU8brNliTORSYBZPOwdt8anp9RvuCM6Uo"
)
```

## 📦 Key Integrations

### 1. Product Fetching
```python
# Get all active products
response = supabase.table("products").select("*").eq("is_active", True).execute()
products = response.data

# Get single product by product_id
response = supabase.table("products").select("*").eq("product_id", "D1").single().execute()
product = response.data
```

### 2. Creating Orders
```python
# Generate order string
response = supabase.rpc("generate_order_string").execute()
order_string = response.data

# Create order
order_data = {
    "order_string": order_string,
    "telegram_user_id": user.id,
    "user_name": "John Doe",
    "phone": "09123456789",
    "address": {
        "house_no": "123",
        "street": "Main St",
        "ward": "Ward 1",
        "township": "Downtown",
        "city": "Yangon"
    },
    "items": [
        {
            "product_id": "D1",
            "product_name": "Product Name",
            "quantity": 2,
            "price": 10.00
        }
    ],
    "total_cost": 20.00,
    "delivery_type": "express_cars",  # or "delivery_company"
    "payment_image_url": "https://storage-url/payment.jpg",
    "status": "pending"
}

response = supabase.table("orders").insert(order_data).execute()
```

### 3. Upload Payment Screenshot
```python
# Upload to Supabase Storage
with open("payment_screenshot.jpg", "rb") as f:
    response = supabase.storage.from_("payment-screenshots").upload(
        f"telegram_{user_id}_{order_id}.jpg",
        f,
        {"content-type": "image/jpeg"}
    )

# Get public URL
payment_url = supabase.storage.from_("payment-screenshots").get_public_url(
    f"telegram_{user_id}_{order_id}.jpg"
)
```

### 4. User Management
```python
# Check if user is banned
response = supabase.table("profiles").select("is_banned").eq("telegram_user_id", user.id).maybe_single().execute()
if response.data and response.data["is_banned"]:
    # User is banned, deny access
    pass
```

### 5. Deep Links
When a user clicks a deep link like `https://t.me/yourbot?start=D1`:

```python
@bot.message_handler(commands=['start'])
def start(message):
    # Extract product_id from command
    args = message.text.split()
    if len(args) > 1:
        product_id = args[1]
        
        # Fetch product from database
        response = supabase.table("products").select("*").eq("product_id", product_id).single().execute()
        product = response.data
        
        # Show product details to user
        bot.send_message(
            message.chat.id,
            f"Product: {product['name']}\nPrice: ${product['price']}\nStock: {product['stock']}"
        )
```

### 6. Broadcast Messages
```python
# Check for new broadcast messages
response = supabase.table("broadcast_messages").select("*").order("sent_at", desc=True).limit(10).execute()
messages = response.data

# Send to all users
for msg in messages:
    # Get all non-banned users
    users_response = supabase.table("profiles").select("telegram_user_id").eq("is_banned", False).execute()
    
    for user in users_response.data:
        if user["telegram_user_id"]:
            bot.send_message(user["telegram_user_id"], msg["message"])
```

### 7. Order Status Updates
Listen for order approvals/rejections using Supabase Realtime:

```python
# Subscribe to order changes
def handle_order_update(payload):
    order = payload["new"]
    telegram_user_id = order["telegram_user_id"]
    
    if order["status"] == "approved":
        bot.send_message(telegram_user_id, f"✅ Your order {order['order_string']} has been approved and sent to delivery!")
    elif order["status"] == "rejected":
        bot.send_message(telegram_user_id, f"❌ Your order {order['order_string']} was rejected. Please contact support.")

# Set up realtime subscription
supabase.table("orders").on("UPDATE", handle_order_update).subscribe()
```

## 🎯 Complete Order Flow

1. **User starts bot** → Check if banned
2. **User browses products** → Fetch from `products` table
3. **User selects product** → Show details
4. **User creates order** → Collect info step-by-step
5. **User uploads payment** → Upload to storage bucket
6. **Create order record** → Insert into `orders` table with `status="pending"`
7. **Admin reviews** → Admin panel shows order
8. **Admin approves/rejects** → Status updated in database
9. **Bot notifies user** → Via realtime subscription or polling

## 🔒 Security Notes

- Never expose service role key in your bot
- Use anon key for client operations
- RLS policies will protect data
- Payment screenshots are private by default
- Only admins can view payment screenshots

## 📚 Additional Resources

- [Supabase Python Docs](https://supabase.com/docs/reference/python/introduction)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Supabase Storage](https://supabase.com/docs/guides/storage)
- [Supabase Realtime](https://supabase.com/docs/guides/realtime)

## 🚀 Getting Started

1. Create your Telegram bot with BotFather
2. Install required packages: `pip install python-telegram-bot supabase`
3. Connect to Supabase using credentials above
4. Implement order flow using the examples
5. Test with deep links and order creation
6. Monitor orders in the admin panel!