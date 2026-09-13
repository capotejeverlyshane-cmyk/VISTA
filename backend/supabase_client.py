import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load from ../.env (since this is in backend directory, maybe it will pick it up, but let's be safe)
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(env_path)

# Fallback to current directory .env if the above doesn't work
if not os.environ.get("SUPABASE_URL"):
    load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

if not url or not key:
    raise ValueError("Supabase credentials not found. Make sure SUPABASE_URL and SUPABASE_KEY are in your .env file.")

supabase: Client = create_client(url, key)
