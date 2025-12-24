class BaseDataModel:
    """Base class for all data models using Supabase"""

    def __init__(self, supabase_client):
        self.supabase_client = supabase_client
        self.table_name = None
    
    def table(self):
        """Get table reference"""
        return self.supabase_client.table(self.table_name)