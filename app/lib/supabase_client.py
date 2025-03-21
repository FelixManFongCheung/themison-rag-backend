import os
from supabase import create_client, Client
from typing import Optional

supabase_instance: Optional[Client] = None

def supabase_client() -> Optional[Client]:
    global supabase_instance
    
    if supabase_instance is None:
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        supabase_instance = create_client(url, key)
    
    return supabase_instance
    