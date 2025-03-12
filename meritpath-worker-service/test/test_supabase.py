import os
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get Supabase credentials from environment variables
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")

# Create Supabase client
supabase = create_client(supabase_url, supabase_key)

# Test connection with a simple query
try:
    # Try to fetch a single row from a public table
    # Replace "your_table" with a table that exists in your database
    response = supabase.table("job_results").select("*").limit(1).execute()
    print("Connection successful!")
    print(f"Response: {response}")
except Exception as e:
    print(f"Connection failed: {e}")