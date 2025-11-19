#!/usr/bin/env python3
"""
Link admin Supabase account to Telegram ID
"""
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

def link_telegram():
    supabase_url = os.getenv("SUPABASE_URL")
    service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    admin_email = os.getenv("ADMIN_EMAIL")
    
    if not all([supabase_url, service_role_key, admin_email]):
        print("❌ Error: Required environment variables not set")
        return False
    
    print("🔗 Linking Telegram account to admin user")
    print(f"📧 Admin email: {admin_email}")
    
    # Ask for Telegram user ID
    print("\n📱 To find your Telegram user ID:")
    print("1. Open Telegram and search for @userinfobot")
    print("2. Send /start to the bot")
    print("3. It will reply with your user ID")
    print()
    
    telegram_id = input("Enter your Telegram user ID: ").strip()
    
    if not telegram_id.isdigit():
        print("❌ Invalid Telegram ID. Must be a number.")
        return False
    
    telegram_id = int(telegram_id)
    
    try:
        supabase = create_client(supabase_url, service_role_key)
        
        # Get admin user
        print("\n1️⃣ Finding admin user...")
        user_response = supabase.auth.admin.list_users()
        
        user_id = None
        for user in user_response:
            if user.email == admin_email:
                user_id = user.id
                print(f"✅ Found admin user! User ID: {user_id}")
                break
        
        if not user_id:
            print(f"❌ Admin user with email {admin_email} not found")
            return False
        
        # Check if profile already exists
        print("\n2️⃣ Checking existing profile...")
        existing_profile = supabase.table("profiles").select("*").eq("id", user_id).maybe_single().execute()
        
        if existing_profile.data:
            # Update existing profile
            print("📝 Updating existing profile...")
            response = supabase.table("profiles").update({
                "telegram_user_id": telegram_id
            }).eq("id", user_id).execute()
        else:
            # Create new profile
            print("📝 Creating new profile...")
            response = supabase.table("profiles").insert({
                "id": user_id,
                "telegram_user_id": telegram_id,
                "is_banned": False
            }).execute()
        
        if response.data:
            print("✅ Telegram account linked successfully!")
            print(f"\n🎉 Your Telegram ID {telegram_id} is now linked to admin account")
            print(f"You can now use /admin command in the Telegram bot!")
            return True
        else:
            print(f"❌ Failed to link: {response}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("  Link Telegram to Admin Account")
    print("="*60)
    success = link_telegram()
    print("="*60)
    if not success:
        exit(1)
