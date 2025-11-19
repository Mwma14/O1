import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ConversationHandler, filters, ContextTypes
from supabase import create_client, Client
from dotenv import load_dotenv
import json
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import io

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL") or "https://dwaxejcqvtkeavngwrzk.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY") or "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR3YXhlamNxdnRrZWF2bmd3cnprIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjM0NDY2NTIsImV4cCI6MjA3OTAyMjY1Mn0.o5kO7P4lpnQU8brNliTORSYBZPOwdt8anp9RvuCM6Uo"
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_CHANNEL_ID = os.getenv("ADMIN_CHANNEL_ID", "")  # Set this to your admin channel ID

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Payment details
PAYMENT_DETAILS = """
💳 **Payment Details**

**Kpay:** 09883249943
**Wave Pay:** 09883249943

Please send payment and upload the screenshot after payment.
"""

# Conversation states
(QUANTITY, ADD_MORE, NAME_CONFIRM, NAME_EDIT, PHONE_CONFIRM, PHONE_EDIT,  
 HOUSE_NO, STREET, WARD, TOWNSHIP, CITY, ADDRESS_CONFIRM,
 DELIVERY_TYPE, FINAL_CONFIRM, PAYMENT_PHOTO) = range(15)

# Pagination settings
PRODUCTS_PER_PAGE = 5

# Helper function to check if user is banned
async def is_user_banned(telegram_user_id: int) -> bool:
    try:
        response = supabase.table("profiles").select("is_banned").eq("telegram_user_id", telegram_user_id).execute()
        if response.data and len(response.data) > 0 and response.data[0].get("is_banned"):
            return True
        return False
    except Exception as e:
        logger.error(f"Error checking ban status: {e}")
        return False

# Generate PDF receipt
def generate_pdf_receipt(order_data: dict) -> bytes:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Title
    c.setFont("Helvetica-Bold", 20)
    c.drawString(1*inch, height - 1*inch, "ORDER RECEIPT")
    
    # Order details
    c.setFont("Helvetica", 12)
    y = height - 1.5*inch
    
    c.drawString(1*inch, y, f"Order ID: {order_data.get('order_string', 'N/A')}")
    y -= 0.3*inch
    c.drawString(1*inch, y, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    y -= 0.5*inch
    
    # Customer info
    c.setFont("Helvetica-Bold", 14)
    c.drawString(1*inch, y, "Customer Information")
    y -= 0.3*inch
    c.setFont("Helvetica", 12)
    c.drawString(1*inch, y, f"Name: {order_data.get('user_name', 'N/A')}")
    y -= 0.25*inch
    c.drawString(1*inch, y, f"Phone: {order_data.get('phone', 'N/A')}")
    y -= 0.25*inch
    
    address = order_data.get('address', {})
    if isinstance(address, str):
        address = json.loads(address)
    addr_str = f"{address.get('house_no', '')}, {address.get('street', '')}, {address.get('ward', '')}, {address.get('township', '')}, {address.get('city', '')}"
    c.drawString(1*inch, y, f"Address: {addr_str}")
    y -= 0.5*inch
    
    # Items
    c.setFont("Helvetica-Bold", 14)
    c.drawString(1*inch, y, "Order Items")
    y -= 0.3*inch
    c.setFont("Helvetica", 12)
    
    items = order_data.get('items', [])
    if isinstance(items, str):
        items = json.loads(items)
    
    for item in items:
        c.drawString(1*inch, y, f"• {item['product_name']} x {item['quantity']} - {float(item['price']) * item['quantity']:.2f}")
        y -= 0.25*inch
    
    y -= 0.3*inch
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1*inch, y, f"Delivery Type: {order_data.get('delivery_type', 'N/A').replace('_', ' ').title()}")
    y -= 0.3*inch
    c.setFont("Helvetica-Bold", 14)
    c.drawString(1*inch, y, f"TOTAL: {order_data.get('total_cost', 0):.2f}")
    
    c.save()
    buffer.seek(0)
    return buffer.getvalue()

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    telegram_user_id = user.id
    
    if await is_user_banned(telegram_user_id):
        await update.message.reply_text("❌ You have been banned from using this bot. Please contact support.")
        return
    
    # Check for deep link with product ID
    args = context.args
    if args and len(args) > 0:
        product_id = args[0]
        try:
            response = supabase.table("products").select("*").eq("product_id", product_id).eq("is_active", True).single().execute()
            product = response.data
            
            keyboard = [
                [InlineKeyboardButton("🛒 Order This Product", callback_data=f"order_{product_id}")],
                [InlineKeyboardButton("📦 Browse All Products", callback_data="browse_products_0")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            message = f"""
📦 *{product['name']}*
🆔 Product ID: {product['product_id']}

{product['description'] or 'No description available'}

💰 Price: {product['price']}
📊 Stock: {product['stock']} units

Click below to order this product!
"""
            await update.message.reply_text(message, parse_mode='Markdown', reply_markup=reply_markup)
            return
        except Exception as e:
            logger.error(f"Error fetching product: {e}")
    
    # Main menu
    keyboard = [
        [InlineKeyboardButton("📦 Check Products", callback_data="browse_products_0")],
        [InlineKeyboardButton("🛍️ My Orders", callback_data="my_orders")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_message = f"""
👋 Welcome {user.first_name}!

🎁 *Telegram Order Bot*

I can help you browse products and place orders easily.

Choose an option below to get started:
"""
    
    await update.message.reply_text(welcome_message, parse_mode='Markdown', reply_markup=reply_markup)

# Browse products with pagination
async def browse_products(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 0):
    try:
        response = supabase.table("products").select("*").eq("is_active", True).execute()
        products = response.data
        
        if not products:
            message = "No products available at the moment."
            if update.callback_query:
                await update.callback_query.edit_message_text(message)
            else:
                await update.message.reply_text(message)
            return
        
        # Pagination
        total_products = len(products)
        total_pages = (total_products + PRODUCTS_PER_PAGE - 1) // PRODUCTS_PER_PAGE
        start_idx = page * PRODUCTS_PER_PAGE
        end_idx = min(start_idx + PRODUCTS_PER_PAGE, total_products)
        page_products = products[start_idx:end_idx]
        
        keyboard = []
        for product in page_products:
            keyboard.append([InlineKeyboardButton(
                f"{product['name']} - {product['price']}",
                callback_data=f"product_{product['product_id']}"
            )])
        
        # Pagination buttons
        nav_buttons = []
        if page > 0:
            nav_buttons.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"browse_products_{page-1}"))
        if page < total_pages - 1:
            nav_buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"browse_products_{page+1}"))
        
        if nav_buttons:
            keyboard.append(nav_buttons)
        
        keyboard.append([InlineKeyboardButton("« Back to Menu", callback_data="back_to_menu")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = f"📦 *Available Products* (Page {page+1}/{total_pages})\n\nSelect a product to view details:"
        
        if update.callback_query:
            await update.callback_query.edit_message_text(message, parse_mode='Markdown', reply_markup=reply_markup)
        else:
            await update.message.reply_text(message, parse_mode='Markdown', reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"Error fetching products: {e}")
        message = "Error fetching products. Please try again later."
        if update.callback_query:
            await update.callback_query.edit_message_text(message)
        else:
            await update.message.reply_text(message)

# Show product details
async def show_product_detail(update: Update, context: ContextTypes.DEFAULT_TYPE, product_id: str):
    try:
        response = supabase.table("products").select("*").eq("product_id", product_id).single().execute()
        product = response.data
        
        keyboard = [
            [InlineKeyboardButton("🛒 Order Now", callback_data=f"order_{product_id}")],
            [InlineKeyboardButton("« Back to Products", callback_data="browse_products_0")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = f"""
📦 *{product['name']}*
🆔 Product ID: {product['product_id']}

{product['description'] or 'No description available'}

💰 Price: {product['price']}
📊 Stock: {product['stock']} units
"""
        
        await update.callback_query.edit_message_text(message, parse_mode='Markdown', reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"Error fetching product detail: {e}")
        await update.callback_query.edit_message_text("Error fetching product details.")

# Handle quantity input
async def get_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        quantity = int(update.message.text)
        product = context.user_data.get('current_product')
        
        if quantity <= 0 or quantity > product['stock']:
            await update.message.reply_text(f"Invalid quantity. Please enter a number between 1 and {product['stock']}.")
            return QUANTITY
        
        # Add to cart
        cart_item = {
            'product_id': product['product_id'],
            'product_name': product['name'],
            'quantity': quantity,
            'price': float(product['price'])
        }
        context.user_data['cart'].append(cart_item)
        
        # Ask if user wants to add more products
        keyboard = [
            [InlineKeyboardButton("✅ Yes, Add More", callback_data="add_more_yes")],
            [InlineKeyboardButton("❌ No, Continue to Checkout", callback_data="add_more_no")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        total = sum(item['quantity'] * item['price'] for item in context.user_data['cart'])
        
        await update.message.reply_text(
            f"✅ Added {quantity} x {product['name']} to cart\n"
            f"💰 Subtotal: {total:.2f}\n\n"
            "Do you want to add more products?",
            reply_markup=reply_markup
        )
        return ADD_MORE
    except ValueError:
        await update.message.reply_text("Please enter a valid number.")
        return QUANTITY

# Handle add more products
async def handle_add_more(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "add_more_yes":
        await browse_products(update, context, 0)
        return ConversationHandler.END
    else:
        # Continue to name input
        await query.edit_message_text("Please enter your full name:")
        return NAME_CONFIRM

# Get name
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['user_name'] = update.message.text
    
    keyboard = [
        [InlineKeyboardButton("✅ Correct", callback_data="name_correct")],
        [InlineKeyboardButton("✏️ Wrong (Edit)", callback_data="name_wrong")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"Your name: *{update.message.text}*\n\nIs this correct?",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )
    return NAME_CONFIRM

# Confirm name
async def confirm_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "name_correct":
        await query.edit_message_text("Please enter your phone number:")
        return PHONE_CONFIRM
    else:
        await query.edit_message_text("Please enter your correct name:")
        return NAME_EDIT

# Edit name
async def edit_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['user_name'] = update.message.text
    
    keyboard = [
        [InlineKeyboardButton("✅ Correct", callback_data="name_correct")],
        [InlineKeyboardButton("✏️ Wrong (Edit)", callback_data="name_wrong")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"Your name: *{update.message.text}*\n\nIs this correct?",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )
    return NAME_CONFIRM

# Get phone
async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['phone'] = update.message.text
    
    keyboard = [
        [InlineKeyboardButton("✅ Correct", callback_data="phone_correct")],
        [InlineKeyboardButton("✏️ Wrong (Edit)", callback_data="phone_wrong")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"Your phone: *{update.message.text}*\n\nIs this correct?",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )
    return PHONE_CONFIRM

# Confirm phone
async def confirm_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "phone_correct":
        await query.edit_message_text("Please enter your house/building number:")
        return HOUSE_NO
    else:
        await query.edit_message_text("Please enter your correct phone number:")
        return PHONE_EDIT

# Edit phone
async def edit_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['phone'] = update.message.text
    
    keyboard = [
        [InlineKeyboardButton("✅ Correct", callback_data="phone_correct")],
        [InlineKeyboardButton("✏️ Wrong (Edit)", callback_data="phone_wrong")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"Your phone: *{update.message.text}*\n\nIs this correct?",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )
    return PHONE_CONFIRM

# Get house number
async def get_house_no(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['house_no'] = update.message.text
    await update.message.reply_text("Please enter your street name:")
    return STREET

# Get street
async def get_street(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['street'] = update.message.text
    await update.message.reply_text("Please enter your ward (quarter):")
    return WARD

# Get ward
async def get_ward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['ward'] = update.message.text
    await update.message.reply_text("Please enter your township:")
    return TOWNSHIP

# Get township
async def get_township(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['township'] = update.message.text
    await update.message.reply_text("Please enter your city:")
    return CITY

# Get city and confirm address
async def get_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['city'] = update.message.text
    
    address_str = f"{context.user_data['house_no']}, {context.user_data['street']}, {context.user_data['ward']}, {context.user_data['township']}, {context.user_data['city']}"
    
    keyboard = [
        [InlineKeyboardButton("✅ Correct", callback_data="address_correct")],
        [InlineKeyboardButton("✏️ Wrong (Re-enter)", callback_data="address_wrong")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"Your address:\n*{address_str}*\n\nIs this correct?",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )
    return ADDRESS_CONFIRM

# Confirm address
async def confirm_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "address_correct":
        keyboard = [
            [InlineKeyboardButton("🚗 Express Cars", callback_data="delivery_express_cars")],
            [InlineKeyboardButton("🚚 Delivery Company", callback_data="delivery_delivery_company")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "Please select your delivery type:",
            reply_markup=reply_markup
        )
        return DELIVERY_TYPE
    else:
        await query.edit_message_text("Please enter your house/building number again:")
        return HOUSE_NO

# Handle delivery type and show final confirmation
async def handle_delivery_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    delivery_type = query.data.removeprefix("delivery_")
    context.user_data['delivery_type'] = delivery_type
    
    # Show final confirmation
    cart = context.user_data.get('cart', [])
    total_cost = sum(item['quantity'] * item['price'] for item in cart)
    
    items_str = "\n".join([f"• {item['product_name']} x {item['quantity']} - {item['price'] * item['quantity']:.2f}" for item in cart])
    address_str = f"{context.user_data['house_no']}, {context.user_data['street']}, {context.user_data['ward']}, {context.user_data['township']}, {context.user_data['city']}"
    
    confirmation_message = f"""
📋 *ORDER SUMMARY*

*Items:*
{items_str}

*Total Cost:* {total_cost:.2f}

*Customer Info:*
Name: {context.user_data['user_name']}
Phone: {context.user_data['phone']}
Address: {address_str}

*Delivery Type:* {delivery_type.replace('_', ' ').title()}

Confirm all details are correct?
"""
    
    keyboard = [
        [InlineKeyboardButton("✅ Yes, Confirm", callback_data="final_confirm_yes")],
        [InlineKeyboardButton("✏️ No, Edit Details", callback_data="final_confirm_no")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(confirmation_message, parse_mode='Markdown', reply_markup=reply_markup)
    return FINAL_CONFIRM

# Handle final confirmation
async def handle_final_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "final_confirm_yes":
        # Show payment details
        cart = context.user_data.get('cart', [])
        total_cost = sum(item['quantity'] * item['price'] for item in cart)
        
        await query.edit_message_text(
            f"{PAYMENT_DETAILS}\n\n💰 *Total Amount: {total_cost:.2f}*\n\n"
            "Please upload your payment screenshot after making the payment.",
            parse_mode='Markdown'
        )
        return PAYMENT_PHOTO
    else:
        # Let user edit details
        keyboard = [
            [InlineKeyboardButton("👤 Edit Name", callback_data="edit_name")],
            [InlineKeyboardButton("📞 Edit Phone", callback_data="edit_phone")],
            [InlineKeyboardButton("📍 Edit Address", callback_data="edit_address")],
            [InlineKeyboardButton("🛒 Edit Products", callback_data="edit_products")],
            [InlineKeyboardButton("🚚 Edit Delivery Type", callback_data="edit_delivery")],
            [InlineKeyboardButton("« Back to Confirmation", callback_data="back_to_confirm")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text("What would you like to edit?", reply_markup=reply_markup)
        return FINAL_CONFIRM

# Handle payment photo
async def get_payment_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    if not update.message.photo:
        await update.message.reply_text("Please send a photo of your payment screenshot.")
        return PAYMENT_PHOTO
    
    try:
        photo = update.message.photo[-1]
        
        # Generate order string
        order_string_response = supabase.rpc("generate_order_string").execute()
        order_string = order_string_response.data
        
        # Create order
        cart = context.user_data.get('cart', [])
        total_cost = sum(item['quantity'] * item['price'] for item in cart)
        
        # Prepare address as dict (Supabase handles JSONB serialization)
        address_json = {
            "house_no": context.user_data['house_no'],
            "street": context.user_data['street'],
            "ward": context.user_data['ward'],
            "township": context.user_data['township'],
            "city": context.user_data['city']
        }
        
        order_data = {
            "order_string": order_string,
            "telegram_user_id": user.id,
            "user_name": context.user_data['user_name'],
            "phone": context.user_data['phone'],
            "address": address_json,
            "items": cart,
            "total_cost": float(total_cost),
            "delivery_type": context.user_data['delivery_type'],
            "status": "pending"
        }
        
        # Save order (use count='none' to avoid RLS error on SELECT after INSERT)
        logger.info(f"Attempting to save order: {order_string}")
        logger.info(f"Order cart items being saved: {cart}")
        insert_response = supabase.table("orders").insert(order_data, count='none').execute()
        logger.info(f"Order saved successfully: {order_string}")
        
        # Generate PDF
        pdf_bytes = generate_pdf_receipt(order_data)
        
        # Send PDF to user
        await update.message.reply_document(
            document=io.BytesIO(pdf_bytes),
            filename=f"receipt_{order_string}.pdf",
            caption=f"✅ Order placed successfully!\n\n📝 Order ID: {order_string}"
        )
        
        # Send order to admin channel
        if ADMIN_CHANNEL_ID:
            items_str = "\n".join([f"• {item['product_name']} x {item['quantity']} - {item['price'] * item['quantity']:.2f}" for item in cart])
            address_str = f"{address_json['house_no']}, {address_json['street']}, {address_json['ward']}, {address_json['township']}, {address_json['city']}"
            
            admin_message = f"""
🆕 *NEW ORDER RECEIVED*

📝 Order ID: `{order_string}`
👤 Customer: {order_data['user_name']}
📞 Phone: {order_data['phone']}
📍 Address: {address_str}

🛒 *Items:*
{items_str}

💰 *Total:* {total_cost:.2f}
🚚 *Delivery:* {order_data['delivery_type'].replace('_', ' ').title()}
"""
            
            keyboard = [
                [InlineKeyboardButton("✅ Approve", callback_data=f"approve_{order_string}")],
                [InlineKeyboardButton("❌ Reject", callback_data=f"reject_{order_string}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Send message
            await context.bot.send_message(
                chat_id=ADMIN_CHANNEL_ID,
                text=admin_message,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
            # Send payment screenshot
            await context.bot.send_photo(
                chat_id=ADMIN_CHANNEL_ID,
                photo=photo.file_id,
                caption="Payment Screenshot"
            )
            
            # Send PDF
            await context.bot.send_document(
                chat_id=ADMIN_CHANNEL_ID,
                document=io.BytesIO(pdf_bytes),
                filename=f"receipt_{order_string}.pdf"
            )
        
        # Save user profile
        profile_data = {
            "telegram_user_id": user.id,
            "username": user.username,
            "phone": context.user_data['phone']
        }
        
        try:
            existing = supabase.table("profiles").select("*").eq("telegram_user_id", user.id).maybe_single().execute()
            if not existing.data:
                supabase.table("profiles").insert(profile_data).execute()
        except:
            pass
        
        await update.message.reply_text(
            f"✅ Order placed successfully!\n\n"
            f"📝 Order ID: {order_string}\n"
            f"💰 Total: {total_cost:.2f}\n\n"
            "Your order is pending approval. You will be notified once it's approved!"
        )
        
        # Clear cart
        context.user_data.clear()
        
        return ConversationHandler.END
    except Exception as e:
        logger.error(f"Error processing order: {e}", exc_info=True)
        await update.message.reply_text(f"Error processing your order. Please try again later.\n\nError details: {str(e)}")  
        return ConversationHandler.END

# Handle admin approval/rejection
async def handle_admin_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    action, order_string = query.data.split("_", 1)
    
    try:
        # Get order details
        order = supabase.table("orders").select("*").eq("order_string", order_string).single().execute()
        order_data = order.data
        
        if action == "approve":
            # Update order status with approval timestamp
            from datetime import datetime, timezone
            supabase.table("orders").update({
                "status": "approved",
                "approved_at": datetime.now(timezone.utc).isoformat()
            }).eq("order_string", order_string).execute()
            
            # Notify user
            await context.bot.send_message(
                chat_id=order_data['telegram_user_id'],
                text=f"✅ Your order #{order_string} has been approved and sent to delivery!"
            )
            
            await query.edit_message_text(
                f"{query.message.text}\n\n✅ *APPROVED*",
                parse_mode='Markdown'
            )
        else:
            # Update order status with rejection reason
            supabase.table("orders").update({
                "status": "rejected",
                "rejection_reason": "Rejected via Telegram admin channel"
            }).eq("order_string", order_string).execute()
            
            # Notify user
            await context.bot.send_message(
                chat_id=order_data['telegram_user_id'],
                text=f"❌ Your order #{order_string} has been rejected. Please contact admin for more information."
            )
            
            await query.edit_message_text(
                f"{query.message.text}\n\n❌ *REJECTED*",
                parse_mode='Markdown'
            )
    except Exception as e:
        logger.error(f"Error handling admin action: {e}")
        await query.edit_message_text("Error processing action.")

# View my orders
async def my_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    try:
        response = supabase.table("orders").select("*").eq("telegram_user_id", user.id).order("created_at", desc=True).limit(10).execute()
        orders = response.data
        
        if not orders:
            message = "You haven't placed any orders yet."
        else:
            message = "📋 *Your Recent Orders*\n\n"
            for order in orders:
                status_emoji = {
                    "pending": "⏳",
                    "approved": "✅",
                    "rejected": "❌",
                    "delivered": "📦"
                }.get(order['status'], "❓")
                
                message += f"{status_emoji} *{order['order_string']}*\n"
                message += f"Status: {order['status'].title()}\n"
                message += f"Total: {order['total_cost']}\n"
                message += f"Date: {order['created_at'][:10]}\n\n"
        
        if update.callback_query:
            await update.callback_query.edit_message_text(message, parse_mode='Markdown')
        else:
            await update.message.reply_text(message, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error fetching orders: {e}")
        message = "Error fetching your orders."
        if update.callback_query:
            await update.callback_query.edit_message_text(message)
        else:
            await update.message.reply_text(message)

# Help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
ℹ️ *How to Use This Bot*

1️⃣ Browse products using /start or the menu
2️⃣ Select a product to view details
3️⃣ Click "Order Now" to place an order
4️⃣ You can add multiple products to your cart
5️⃣ Fill in your details step by step
6️⃣ Upload payment screenshot
7️⃣ Wait for admin approval

📞 *Commands*
/start - Start the bot
/orders - View your orders
/help - Show this help message

Need support? Contact our team!
"""
    
    if update.callback_query:
        await update.callback_query.edit_message_text(help_text, parse_mode='Markdown')
    else:
        await update.message.reply_text(help_text, parse_mode='Markdown')

# Cancel command
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("Order cancelled. Use /start to begin again.")
    return ConversationHandler.END

# Get Chat ID command (useful for finding channel ID)
async def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    chat_type = update.effective_chat.type
    chat_title = update.effective_chat.title if hasattr(update.effective_chat, 'title') else "Private Chat"
    
    message = f"""
📋 *Chat Information*

Chat ID: `{chat_id}`
Chat Type: {chat_type}
Chat Title: {chat_title}

💡 *Tip:* If this is your admin channel, copy the Chat ID and set it as ADMIN_CHANNEL_ID environment variable in Replit Secrets.
"""
    
    await update.message.reply_text(message, parse_mode='Markdown')

# Admin panel command
async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # You can add admin verification here if needed
    admin_url = "https://1f0e9110-4c8f-4678-a4be-06a5c6e021de-00-2i6rorpjetbsr.worf.replit.dev/admin"
    
    message = f"""
🔐 *Admin Panel*

Access the admin panel to manage:
• Products & Inventory
• Orders & Approvals  
• Users & Permissions
• Broadcast Messages

🔗 *Admin Panel Link:*
{admin_url}

📝 Note: You'll need to login with your authorized admin account.
"""
    
    await update.message.reply_text(message, parse_mode='Markdown')

# Order button handler (for conversation entry)
async def order_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    product_id = query.data.split("_")[1]
    context.user_data['current_product_id'] = product_id
    
    try:
        response = supabase.table("products").select("*").eq("product_id", product_id).single().execute()
        product = response.data
        
        # Initialize cart if not exists
        if 'cart' not in context.user_data:
            context.user_data['cart'] = []
        
        context.user_data['current_product'] = product
        
        message = f"How many {product['name']} would you like to order?\n\nPlease enter a quantity (1-{product['stock']}):"
        await query.edit_message_text(message)
        
        return QUANTITY
    except Exception as e:
        logger.error(f"Error starting order: {e}")
        await query.edit_message_text("Error processing order. Please try again.")
        return ConversationHandler.END

# Navigation callback query handler
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("browse_products_"):
        page = int(query.data.split("_")[-1])
        await browse_products(update, context, page)
    elif query.data.startswith("product_"):
        product_id = query.data.split("_")[1]
        await show_product_detail(update, context, product_id)
    elif query.data == "my_orders":
        await my_orders(update, context)
    elif query.data == "help":
        await help_command(update, context)
    elif query.data == "back_to_menu":
        await start(update, context)
    elif query.data.startswith("approve_") or query.data.startswith("reject_"):
        await handle_admin_action(update, context)

def main():
    if not BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables!")
        return
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.error("SUPABASE_URL and SUPABASE_ANON_KEY must be set in environment variables!")
        return
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Conversation handler for orders
    conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(order_button_handler, pattern='^order_'),
            CallbackQueryHandler(handle_add_more, pattern='^add_more_')
        ],
        states={
            QUANTITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_quantity)],
            ADD_MORE: [CallbackQueryHandler(handle_add_more, pattern='^add_more_')],
            NAME_CONFIRM: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_name),
                CallbackQueryHandler(confirm_name, pattern='^name_')
            ],
            NAME_EDIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_name)],
            PHONE_CONFIRM: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone),
                CallbackQueryHandler(confirm_phone, pattern='^phone_')
            ],
            PHONE_EDIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_phone)],
            HOUSE_NO: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_house_no)],
            STREET: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_street)],
            WARD: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_ward)],
            TOWNSHIP: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_township)],
            CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_city)],
            ADDRESS_CONFIRM: [CallbackQueryHandler(confirm_address, pattern='^address_')],
            DELIVERY_TYPE: [CallbackQueryHandler(handle_delivery_type, pattern='^delivery_')],
            FINAL_CONFIRM: [CallbackQueryHandler(handle_final_confirm, pattern='^final_confirm_')],
            PAYMENT_PHOTO: [MessageHandler(filters.PHOTO, get_payment_photo)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("orders", my_orders))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(CommandHandler("getchatid", get_chat_id))
    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(button_callback))
    
    logger.info("Bot started successfully!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
