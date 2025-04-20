from supabase import create_client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_supabase():
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not supabase_key:
        print(f"Debug - SUPABASE_URL: {supabase_url}")
        print(f"Debug - SUPABASE_KEY exists: {'yes' if supabase_key else 'no'}")
        raise Exception("Missing Supabase environment variables")
    
    try:
        client = create_client(supabase_url, supabase_key)
        # Test the connection
        client.table("tweet_analysis").select("*").limit(1).execute()
        return client
    except Exception as e:
        print(f"Error initializing Supabase client: {str(e)}")
        raise

# Initialize Supabase client
try:
    supabase = get_supabase()
except Exception as e:
    print(f"Failed to initialize Supabase client: {str(e)}")
    raise

def init_supabase():
    try:
        # Create tables if they don't exist
        supabase.table("tweet_analysis").select("*").limit(1).execute()
        print("Supabase connection successful")
    except Exception as e:
        print(f"Supabase initialization error: {str(e)}")
        raise 