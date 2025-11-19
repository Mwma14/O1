#!/usr/bin/env python3
"""
Grant admin role to existing user
"""
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

def grant_admin_role():
    supabase_url = os.getenv("SUPABASE_URL")
    service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    admin_email = os.getenv("ADMIN_EMAIL")
    
    if not all([supabase_url, service_role_key, admin_email]):
        print("❌ Error: Required environment variables not set")
        return False
    
    print(f"🔧 Granting admin role to: {admin_email}")
    
    try:
        supabase = create_client(supabase_url, service_role_key)
        
        # Get user by email
        print("\n1️⃣ Finding user...")
        user_response = supabase.auth.admin.list_users()
        
        user_id = None
        for user in user_response:
            if user.email == admin_email:
                user_id = user.id
                print(f"✅ Found user! User ID: {user_id}")
                break
        
        if not user_id:
            print(f"❌ User with email {admin_email} not found")
            print("Please sign up first at /auth page")
            return False
        
        # Check if already has admin role
        print("\n2️⃣ Checking current role...")
        existing_role = supabase.table("user_roles").select("*").eq("user_id", user_id).eq("role", "admin").execute()
        
        if existing_role.data:
            print("✅ User already has admin role!")
            print(f"\n🎉 You can login at /auth with:")
            print(f"   Email: {admin_email}")
            return True
        
        # Add admin role
        print("\n3️⃣ Granting admin role...")
        role_response = supabase.table("user_roles").insert({
            "user_id": user_id,
            "role": "admin"
        }).execute()
        
        if role_response.data:
            print("✅ Admin role granted successfully!")
            print(f"\n🎉 You can now login at /auth with:")
            print(f"   Email: {admin_email}")
            return True
        else:
            print(f"❌ Failed to grant role: {role_response}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("  Grant Admin Role")
    print("="*60)
    success = grant_admin_role()
    print("="*60)
    if not success:
        exit(1)
