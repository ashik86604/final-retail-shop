import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('FLASK_DEBUG', True)

class SupabaseConfig:
    """Supabase configuration"""
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')
    
    @staticmethod
    def validate():
        if not SupabaseConfig.SUPABASE_URL or not SupabaseConfig.SUPABASE_KEY:
            raise ValueError("Supabase credentials missing in .env file")

class NvidiaConfig:
    """NVIDIA API configuration"""
    NVIDIA_API_KEY = os.getenv('NVIDIA_API_KEY', '')