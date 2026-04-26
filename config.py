"""
Configuration settings for Online Exam Portal
Contains database credentials, secret keys, and application settings
"""

import os

class Config:
    """Base configuration class"""
    
    # Secret key for session management
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production-2024'
    
    # Database configuration
    DB_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': '@RAJPUTNishant2005',
        'database': 'online_exam_portal',
        'raise_on_warnings': True,
        'autocommit': False
    }
    
    # SIMPLIFIED Session configuration
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    PERMANENT_SESSION_LIFETIME = 3600
    
    # Application settings
    DEBUG = True
    TESTING = False
    
    # Security settings
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Upload Settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    
    # Pagination settings
    RESULTS_PER_PAGE = 10
    
    # Exam settings
    MIN_EXAM_DURATION = 5
    MAX_EXAM_DURATION = 180
    MIN_QUESTIONS_PER_EXAM = 1
    MAX_QUESTIONS_PER_EXAM = 100


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    DB_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'online_exam_portal_test',
        'raise_on_warnings': True,
        'autocommit': False
    }


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}