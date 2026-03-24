"""
Setup script to create the first admin user
Run this once to initialize the system
"""

from supabase_client import get_supabase
from datetime import datetime

supabase = get_supabase()

def create_admin():
    """Create first admin user"""
    
    email = "admin@retailhub.com"
    password = "Admin@12345"  # Change this!
    full_name = "Super Admin"
    
    print("🔧 Setting up RetailHub Admin User...")
    print(f"Email: {email}")
    print(f"Password: {password}")
    print()
    
    try:
        # Check if user already exists
        existing = supabase.table('users').select('*').eq('email', email).execute()
        if existing.data:
            print("⚠️ Admin user already exists!")
            print(f"Email: {existing.data[0]['email']}")
            print(f"Role: {existing.data[0]['role']}")
            return
        
        # Create auth user
        print("📝 Creating auth user...")
        auth_response = supabase.auth.sign_up({
            'email': email,
            'password': password,
            'options': {
                'data': {
                    'full_name': full_name,
                    'role': 'admin'
                }
            }
        })
        
        if auth_response.user:
            user_id = str(auth_response.user.id)
            print(f"✅ Auth user created: {user_id}")
            
            # Create user profile
            print("📋 Creating user profile...")
            supabase.table('users').insert({
                'id': user_id,
                'email': email,
                'full_name': full_name,
                'role': 'admin',
                'created_at': datetime.utcnow().isoformat()
            }).execute()
            
            print(f"✅ User profile created!")
            print()
            print("=" * 50)
            print("🎉 ADMIN USER CREATED SUCCESSFULLY!")
            print("=" * 50)
            print(f"Email: {email}")
            print(f"Password: {password}")
            print(f"Role: admin")
            print()
            print("⚠️  IMPORTANT:")
            print("1. Save these credentials in a safe place")
            print("2. Change the password after first login")
            print("3. Do NOT share this password")
            print("=" * 50)
        else:
            print("❌ Failed to create auth user")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == '__main__':
    create_admin()
#Email: admin@retailhub.com
# Password: Admin@12345
# Role: admin