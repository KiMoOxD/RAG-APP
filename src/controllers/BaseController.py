from helpers.config import get_settings, Settings
import random 
import string


class BaseController:
    """Base controller class"""
    
    def __init__(self):
        self.app_settings: Settings = get_settings()
    
    def generate_random_string(self, length: int = 12):
        """Generate a random alphanumeric string"""
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))