# test_connection.py (put this in your root folder)
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

print("URL:", url)
print("KEY length:", len(key) if key else 0)

client = create_client(url, key)
result = client.table("clients").select("id").limit(1).execute()
print("Result:", result)