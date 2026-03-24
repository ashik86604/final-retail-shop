import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get credentials from .env
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

# Validate credentials exist
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError(
        "❌ Missing Supabase credentials!\n"
        "Please add SUPABASE_URL and SUPABASE_KEY to your .env file\n"
        "Get them from: https://app.supabase.com/project/[project-id]/settings/api"
    )

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_supabase():
    """Return Supabase client"""
    return supabase