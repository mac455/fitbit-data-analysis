import os 
from dotenv import load_dotenv, find_dotenv
from supabase import create_client, Client 

load_dotenv(find_dotenv())

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# --- TEMPORARY DEBUG ---
print("URL:", SUPABASE_URL)
print("KEY (first 20 chars):", SUPABASE_KEY[:20] if SUPABASE_KEY else "NOT FOUND")
print("KEY length:", len(SUPABASE_KEY) if SUPABASE_KEY else 0)
print("KEY repr:", repr(SUPABASE_KEY))
# --- END DEBUG ---

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError(f"Missing Credentials! URL found: {SUPABASE_URL}, Key loaded: {True if SUPABASE_KEY else False}")

# Initialise supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)