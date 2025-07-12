import os
from supabase import create_client, Client

class AuthManagerError(Exception):
    pass

class AuthManager:
    def __init__(self):
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_KEY")
        if not supabase_url or not supabase_key:
            raise AuthManagerError("SUPABASE_URL and SUPABASE_KEY environment variables must be set.")
        try:
            self.supabase: Client = create_client(supabase_url, supabase_key)
        except Exception as e:
            raise AuthManagerError(f"Supabase client could not be initialized: {e}")

    # ... rest of the class ...
