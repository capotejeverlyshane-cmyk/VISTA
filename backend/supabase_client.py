import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Try loading .env from backend directory, parent directory, or current directory
backend_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(backend_dir)
load_dotenv(os.path.join(backend_dir, '.env'))
load_dotenv(os.path.join(parent_dir, '.env'))
load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

if not url or not key:
    raise ValueError("Supabase credentials not found. Make sure SUPABASE_URL and SUPABASE_KEY are in your .env file.")

supabase: Client = create_client(url, key)
