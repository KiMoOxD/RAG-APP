from .BaseDataModel import BaseDataModel
from .db_schemes import Asset
import logging

logger = logging.getLogger(__name__)


class AssetModel(BaseDataModel):
    """Asset model using Supabase PostgreSQL"""

    def __init__(self, supabase_client):
        super().__init__(supabase_client=supabase_client)
        self.table_name = "assets"

    @classmethod
    async def create_instance(cls, db_client):
        """Factory method to create AssetModel instance"""
        instance = cls(db_client)
        return instance

    async def create_asset(self, asset: Asset) -> Asset:
        """Create a new asset in the database"""
        try:
            result = self.table().insert(asset.to_db_dict()).execute()
            
            if result.data and len(result.data) > 0:
                asset.id = result.data[0].get("id")
                return asset
            return None
        except Exception as e:
            logger.error(f"Error creating asset: {e}")
            raise

    async def get_all_project_assets(self, asset_project_id: str, asset_type: str):
        """Get all assets for a project by type"""
        try:
            result = self.table().select("*").eq(
                "asset_project_id", asset_project_id
            ).eq(
                "asset_type", asset_type
            ).execute()
            
            return [
                Asset.from_db_record(record)
                for record in result.data
            ]
        except Exception as e:
            logger.error(f"Error getting project assets: {e}")
            raise

    async def get_asset_record(self, asset_project_id: str, asset_name: str):
        """Get a specific asset by project ID and name"""
        try:
            result = self.table().select("*").eq(
                "asset_project_id", asset_project_id
            ).eq(
                "asset_name", asset_name
            ).execute()
            
            if result.data and len(result.data) > 0:
                return Asset.from_db_record(result.data[0])
            
            return None
        except Exception as e:
            logger.error(f"Error getting asset record: {e}")
            raise

    async def get_asset_by_id(self, asset_id: str):
        """Get asset by its ID"""
        try:
            result = self.table().select("*").eq("id", asset_id).execute()
            
            if result.data and len(result.data) > 0:
                return Asset.from_db_record(result.data[0])
            
            return None
        except Exception as e:
            logger.error(f"Error getting asset by ID: {e}")
            raise

    async def delete_asset(self, asset_id: str) -> bool:
        """Delete an asset by ID"""
        try:
            self.table().delete().eq("id", asset_id).execute()
            return True
        except Exception as e:
            logger.error(f"Error deleting asset: {e}")
            return False