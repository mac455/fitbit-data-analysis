import requests
import os
from dotenv import load_dotenv
import logging

# This logs every HTTP request made
logging.basicConfig(level=logging.DEBUG)

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

headers = {
    "apikey": key,
    "Authorization": f"Bearer {key}"
}
response = requests.get(
    f"{url}/rest/v1/clients?select=*&limit=1",
    headers=headers
)
print(response.status_code)
print(response.json())