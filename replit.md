# Telegram Order Bot with Admin Panel

## Overview

A full-stack order management system consisting of a React-based web admin panel and a Python Telegram bot for customer interactions. The admin panel provides product management, order processing, user management, and broadcast messaging capabilities. The Telegram bot enables customers to browse products, place orders with a guided flow, upload payment screenshots, and track order status. The system uses Supabase for authentication, database, and file storage.

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Changes

**November 19, 2025 (Latest)**
- **Simplified order flow**: Removed Supabase storage for payment screenshots - screenshots now only sent to admin Telegram channel
- **Payment screenshot forwarding**: Orders + payment screenshots + PDF receipts are forwarded directly to admin Telegram channel (ADMIN_CHANNEL_ID)
- **Cleaned Admin Panel**: Removed payment screenshot viewing from web interface - admins view all order details in Telegram channel
- **Database optimization**: Removed payment_image_url field from order data (no longer stored in database)
- **Fixed ban check**: Resolved HTTP 406 error when checking user ban status
- **Deep links verified**: Product sharing via `t.me/yourbot?start=PRODUCT_ID` working correctly

**November 19, 2025 (Earlier)**
- Fixed payment screenshot duplicate error: Added unique timestamp to storage filenames to prevent duplicate key errors when users retry payment screenshot uploads
- Removed all $ currency symbols from bot price displays: Prices now show numeric values only throughout the bot (product listings, cart, order summaries, receipts, admin notifications)
- Previously fixed delivery type bug: Used `.removeprefix()` instead of `.replace()` to prevent enum validation errors

## System Architecture

### Frontend Architecture

**Technology Stack**
- React 18 with TypeScript for type-safe component development
- Vite as the build tool, configured to run on host 0.0.0.0:5000 with proxy support for Replit deployments
- React Router for client-side navigation with a 404 catch-all handler

**UI Components & Styling**
- Shadcn/ui component library built on Radix UI primitives for accessible, composable components
- Tailwind CSS with a custom HSL-based color system defined in CSS variables
- Design tokens include primary, secondary, destructive, success, warning, muted, and accent color schemes
- Responsive design with mobile-first approach

**State Management**
- TanStack Query (React Query) for server state management, caching, and data fetching
- React hooks for local component state
- Supabase Auth for authentication state

**Admin Panel Features**
- Product management: Add, edit, delete products with images
- Order management: View, approve, reject, and mark orders as delivered
- User management: View user profiles, ban/unban functionality
- Broadcast messaging: Send announcements to all active users
- Supabase Auth UI integration for login/signup

### Backend Architecture

**Telegram Bot (Python)**
- Built with `python-telegram-bot` library for handling Telegram updates
- Polling-based architecture for receiving messages and callback queries
- Conversation handler pattern for multi-step order flows

**Bot Features & Flow**
- Product browsing with pagination (5 products per page)
- Deep linking support for direct product access (`t.me/BOT?start=PRODUCT_ID`)
- Multi-step order process: quantity → add more products → name → phone → address (house, street, ward, township, city) → delivery type → payment screenshot
- Order history viewing
- Real-time status notifications (pending, approved, rejected, delivered)
- User ban checking before processing actions
- PDF generation for order receipts using ReportLab

**Conversation States**
- QUANTITY: Collecting product quantity
- ADD_MORE: Option to add more products to cart
- NAME_CONFIRM/NAME_EDIT: Name collection and verification
- PHONE_CONFIRM/PHONE_EDIT: Phone number collection and verification
- HOUSE_NO, STREET, WARD, TOWNSHIP, CITY: Address collection
- ADDRESS_CONFIRM: Address verification
- DELIVERY_TYPE: Express Cars or Delivery Company selection
- PAYMENT_PHOTO: Payment screenshot upload
- FINAL_CONFIRM: Order confirmation

### Database Architecture (Supabase PostgreSQL)

**Tables**
- `products`: Product inventory with product_id, name, description, price, stock, image_url, is_active status
- `orders`: Order records with order_string, telegram_user_id, user details, address (JSON), items (JSON array), total_cost, delivery_type, payment_image_url, status, timestamps
- `profiles`: User profiles with telegram_user_id, username, phone, is_banned flag
- `user_roles`: Admin role assignments (user_id, role)
- `broadcast_messages`: Message history with message content, sent_by, recipient_count

**Row Level Security (RLS)**
- Enabled on all tables for data protection
- Service role key used for admin operations
- Anon key used for public read operations

**Storage Buckets**
- `payment-screenshots`: Private bucket for payment proof images
- `product-images`: Public bucket for product photos

**Database Functions**
- `generate_order_string()`: RPC function for creating unique order identifiers

### Authentication & Authorization

**Supabase Auth**
- Email/password authentication for admin panel
- Email confirmation required for new accounts
- Admin role must be manually granted in `user_roles` table after signup
- Session-based authentication with automatic token refresh

**Telegram User Identification**
- Telegram user ID stored in profiles table
- Optional linking between Supabase accounts and Telegram IDs for admin users

### External Dependencies

**Supabase Cloud Service**
- Project URL: `https://dwaxejcqvtkeavngwrzk.supabase.co`
- PostgreSQL database hosting
- Authentication service
- Storage service for images
- Real-time subscriptions (available but not currently used)

**Telegram Bot API**
- Bot token required from @BotFather
- Webhook or polling modes (currently using polling)
- Inline keyboard support for interactive buttons
- Photo upload/download via Telegram servers

**Third-Party NPM Packages**
- @supabase/supabase-js: Supabase client library
- @supabase/auth-ui-react: Pre-built auth components
- @radix-ui/*: Accessible component primitives
- react-hook-form + zod: Form validation (via @hookform/resolvers)
- class-variance-authority: Component variant management
- tailwind-merge + clsx: Class name utilities
- sonner: Toast notifications
- date-fns: Date formatting

**Python Dependencies**
- python-telegram-bot: Telegram bot framework
- supabase: Supabase Python client
- reportlab: PDF generation
- python-dotenv: Environment variable management

**Deployment Configuration**
- Development server: Vite dev server on port 5000
- Production build: `vite build` with preview on port 5000
- Two separate workflows: Web admin (port 5000) and Telegram bot (background process)
- Environment variables stored in Replit Secrets: TELEGRAM_BOT_TOKEN, SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY, ADMIN_EMAIL, ADMIN_PASSWORD, ADMIN_CHANNEL_ID