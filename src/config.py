"""
Configuration module for WCL Time Splits Analyzer.

This module contains all configuration settings for the application,
including environment-specific configurations for development and production.
"""

import os
from typing import Dict, Any


class Config:
    """Base configuration class."""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # WarcraftLogs API settings
    WCL_API_KEY = os.environ.get('WCL_API_KEY')
    
    # Server settings
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 8080))
    
    # Request settings
    REQUEST_TIMEOUT = int(os.environ.get('REQUEST_TIMEOUT', 30))
    
    # Zone ID mapping for different WoW versions
    ZONE_ID_MAP: Dict[int, str] = {
        # Classic IDs
        1000: "Molten Core",
        1002: "Blackwing Lair",
        1005: "Temple of Ahn'Qiraj",
        1006: "Naxxramas",
        # Season of Discovery / Fresh IDs
        1017: "Blackfathom Deeps",
        1032: "Gnomeregan",
        1034: "Blackwing Lair",
        1035: "Temple of Ahn'Qiraj",
        1036: "Naxxramas",
        # Era IDs
        531: "Temple of Ahn'Qiraj",
        533: "Naxxramas",
    }
    
    # Naxxramas wing configuration for wing clear times
    NAXX_CONFIG: Dict[str, Any] = {
        "wing_bosses": {
            "Spider": {15952, 51116},  # Maexxna
            "Plague": {15954, 51117},  # Loatheb
            "Abomination": {16028, 51118},  # Thaddius
            "Military": {16061, 51113},  # The Four Horsemen
        }
    }


class DevelopmentConfig(Config):
    """Development configuration."""
    
    DEBUG = True
    FLASK_ENV = 'development'


class ProductionConfig(Config):
    """Production configuration."""
    
    DEBUG = False
    FLASK_ENV = 'production'
    
    # Override secret key requirement for production
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    @classmethod
    def validate(cls):
        """Validate production configuration."""
        if not cls.SECRET_KEY:
            raise ValueError("SECRET_KEY environment variable must be set in production")
        if not cls.WCL_API_KEY:
            raise ValueError("WCL_API_KEY environment variable must be set")


class TestingConfig(Config):
    """Testing configuration."""
    
    TESTING = True
    DEBUG = True
    WCL_API_KEY = 'test-api-key'


# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(config_name: str = None) -> Config:
    """Get configuration based on environment."""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    return config.get(config_name, config['default'])
