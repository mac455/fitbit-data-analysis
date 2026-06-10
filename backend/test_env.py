# backend/test_env.py
import os
from dotenv import load_dotenv, find_dotenv

print("1. Current Working Directory:", os.getcwd())
print("2. Looking for .env file location...", find_dotenv())

# Use find_dotenv to auto-scan upward to your root directory
load_dotenv(find_dotenv())

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

print(f"3. Loaded URL from env: {url}")
print(f"4. Loaded Key from env: {key[:15] if key else None}...")