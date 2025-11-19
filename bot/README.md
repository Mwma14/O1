# Telegram Order Bot

This is a complete Telegram bot for order management that integrates with Supabase.

## Features

- 📦 Product browsing with inline keyboards
- 🛒 Complete order flow with step-by-step data collection
- 📸 Payment screenshot upload
- 🚚 Delivery type selection (Express Cars / Delivery Company)
- 📋 Order history viewing
- 🔗 Deep linking support for direct product access
- 🚫 User ban checking
- ✅ Order status notifications (pending/approved/rejected/delivered)

## Setup

1. Create a bot with [@BotFather](https://t.me/botfather) on Telegram
2. Get your bot token
3. Add the token to your Replit Secrets as `TELEGRAM_BOT_TOKEN`
4. The bot will automatically connect to the Supabase database

## Bot Commands

- `/start` - Start the bot and show main menu
- `/products` - Browse all available products
- `/orders` - View your order history
- `/help` - Show help information
- `/cancel` - Cancel current order process

## Deep Linking

Share product links like: `https://t.me/YOUR_BOT?start=PRODUCT_ID`

Example: `https://t.me/YOUR_BOT?start=D1`

## Order Flow

1. User selects a product
2. Enters quantity
3. Provides name and phone
4. Enters complete address (house no, street, ward, township, city)
5. Selects delivery type
6. Uploads payment screenshot
7. Order is created with "pending" status
8. Admin reviews and approves/rejects in the web panel
9. User receives notification about order status

## Database Integration

The bot connects to Supabase and interacts with:
- `products` table - For product listings
- `orders` table - For order management
- `profiles` table - For user data
- `payment-screenshots` storage bucket - For payment images

All database operations respect Row Level Security policies.
