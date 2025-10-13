"""
Configuration loader for portable version
Reads settings from config/settings.ini
"""
import configparser
import os
import sys
from pathlib import Path


def get_base_path():
    """Get base path - works both in dev and as .exe"""
    if getattr(sys, 'frozen', False):
        # Running as compiled exe
        return Path(sys.executable).parent
    else:
        # Running as script
        return Path(__file__).parent


class ConfigLoader:
    """Load configuration from settings.ini"""
    
    def __init__(self):
        self.base_path = get_base_path()
        self.config_file = self.base_path / 'config' / 'settings.ini'
        self.config = configparser.ConfigParser()
        
        if not self.config_file.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_file}")
        
        self.config.read(self.config_file, encoding='utf-8')
    
    def get(self, section, key, default=None):
        """Get config value"""
        try:
            return self.config.get(section, key)
        except:
            return default
    
    def get_bool(self, section, key, default=False):
        """Get boolean config value"""
        value = self.get(section, key)
        if value:
            return value.lower() in ('yes', 'true', '1', 'on')
        return default
    
    def get_int(self, section, key, default=0):
        """Get integer config value"""
        try:
            return int(self.get(section, key, default))
        except:
            return default
    
    def get_path(self, section, key):
        """Get path relative to base path"""
        path_str = self.get(section, key)
        if path_str:
            return self.base_path / path_str
        return None
    
    @property
    def urls(self):
        """Get all URLs"""
        return {
            'alta': self.get('URLS', 'alta'),
            'kontakt_coffee': self.get('URLS', 'kontakt_coffee'),
            'kontakt_toasters': self.get('URLS', 'kontakt_toasters'),
            'elite': self.get('URLS', 'elite'),
            'dimkava': self.get('URLS', 'dimkava'),
        }
    
    @property
    def paths(self):
        """Get all paths"""
        return {
            'base': self.base_path,
            'inventory': self.get_path('PATHS', 'inventory_folder'),
            'output': self.get_path('PATHS', 'output_folder'),
            'logs': self.get_path('PATHS', 'logs_folder'),
            'reports': self.get_path('PATHS', 'output_folder') / 'reports',
            'excel': self.get_path('PATHS', 'output_folder') / 'excel',
        }
    
    @property
    def general(self):
        """Get general settings"""
        return {
            'language': self.get('GENERAL', 'language', 'ru'),
            'create_pdf': self.get_bool('GENERAL', 'create_pdf', True),
            'open_report': self.get_bool('GENERAL', 'open_report', True),
        }
    
    @property
    def timeouts(self):
        """Get timeout settings"""
        return {
            'page_load': self.get_int('TIMEOUTS', 'page_load_timeout', 30),
            'wait_after_load': self.get_int('TIMEOUTS', 'wait_after_load', 3),
            'scroll_pause': self.get_int('TIMEOUTS', 'scroll_pause', 2),
        }
    
    @property
    def expected_products(self):
        """Get expected product counts"""
        return {
            'alta': self.get_int('PARSING', 'expected_alta', 74),
            'kontakt': self.get_int('PARSING', 'expected_kontakt', 30),
            'elite': self.get_int('PARSING', 'expected_elite', 40),
            'dimkava': self.get_int('PARSING', 'expected_dimkava', 41),
        }


if __name__ == '__main__':
    # Test
    config = ConfigLoader()
    print("Base path:", config.base_path)
    print("URLs:", config.urls)
    print("Paths:", config.paths)
    print("General:", config.general)
    print("Timeouts:", config.timeouts)
    print("Expected:", config.expected_products)

