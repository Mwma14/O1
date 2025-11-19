#!/usr/bin/env python3
"""
Setup script to create admin user for the Telegram Order Bot web interface
"""
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

def setup_admin():
    # Get credentials
    supabase_url = os.getenv("SUPABASE_URL")
    service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not service_role_key:
        print("❌ Error: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
        print("\n📝 To fix this:")
        print("1. Go to your Supabase dashboard: https://supabase.com/dashboard")
        print("2. Select your project")
        print("3. Go to Settings → API")
        print("4. Copy the 'service_role' key")
        print("5. Add it to your Replit Secrets as SUPABASE_SERVICE_ROLE_KEY")
        return False
    
    # Get admin credentials from environment variables
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")
    
    if not admin_email or not admin_password:
        print("❌ Error: ADMIN_EMAIL and ADMIN_PASSWORD must be set")
        print("\n📝 Please add these to your Replit Secrets:")
        print("   - ADMIN_EMAIL: Your admin email address")
        print("   - ADMIN_PASSWORD: Your admin password")
        return False
    
    print("🔧 Setting up admin user...")
    print(f"📧 Email: {admin_email}")
    
    try:
        # Create Supabase client with service role key
        supabase = create_client(supabase_url, service_role_key)
        
        # Create the admin user
        print("\n1️⃣ Creating admin user...")
        user_response = supabase.auth.admin.create_user({
            "email": admin_email,
            "password": admin_password,
            "email_confirm": True,  # Auto-confirm email
            "user_metadata": {
                "full_name": "Admin User",
                "role": "admin"
            }
        })
        
        if user_response.user:
            user_id = user_response.user.id
            print(f"✅ User created successfully! User ID: {user_id}")
            
            # Add admin role to user_roles table
            print("\n2️⃣ Granting admin permissions...")
            role_response = supabase.table("user_roles").insert({
                "user_id": user_id,
                "role": "admin"
            }).execute()
            
            if role_response.data:
                print("✅ Admin role granted successfully!")
                print("\n🎉 Setup complete!")
                print(f"\n🌐 You can now login at your web app /auth page with:")
                print(f"   Email: {admin_email}")
                print(f"   Password: {admin_password}")
                return True
            else:
                print("⚠️ User created but role assignment failed")
                print(f"Error: {role_response}")
                return False
        else:
            print("❌ Failed to create user")
            print(f"Response: {user_response}")
            return False
            
    except Exception as e:
        error_msg = str(e)
        if "already registered" in error_msg.lower() or "duplicate" in error_msg.lower():
            print("⚠️ User already exists!")
            print("You can login with your existing credentials at /auth")
            return True
        else:
            print(f"❌ Error: {error_msg}")
            return False

if __name__ == "__main__":
    print("="*60)
    print("  Telegram Order Bot - Admin Setup")
    print("="*60)
    success = setup_admin()
    print("="*60)
    if not success:
        exit(1)
