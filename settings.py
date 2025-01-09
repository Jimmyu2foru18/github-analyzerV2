"""
Configuration Management
-----------------------
Handles configuration loading from environment variables.
provides configuration objects and validation.
"""

import os
import logging
from dataclasses import dataclass
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

from exceptions import ConfigError

logger = logging.getLogger(__name__)

@dataclass
class APIConfig:
    """API configuration settings."""
    openai_api_key: str
    github_api_key: str
    model_name: str = "gpt-4"
    
    @classmethod
    def from_env(cls) -> 'APIConfig':
        """Create API config from environment variables."""
        openai_key = os.getenv('OPENAI_API_KEY')
        github_key = os.getenv('GITHUB_API_KEY')
        
        if not openai_key:
            raise ConfigError("OPENAI_API_KEY")
        if not github_key:
            raise ConfigError("GITHUB_API_KEY")
            
        return cls(
            openai_api_key=openai_key,
            github_api_key=github_key,
            model_name=os.getenv('OPENAI_MODEL', "gpt-4")
        )

@dataclass
class BuildConfig:
    """Build configuration settings."""
    base_download_dir: str = "downloads"
    max_results: int = 5
    min_stars: int = 100
    timeout: int = 300
    parallel_builds: int = 1
    cleanup_after_build: bool = True
    
    @classmethod
    def from_env(cls) -> 'BuildConfig':
        """Create build config from environment variables."""
        try:
            return cls(
                base_download_dir=os.getenv('BUILD_DOWNLOAD_DIR', "downloads"),
                max_results=int(os.getenv('MAX_RESULTS', "5")),
                min_stars=int(os.getenv('MIN_STARS', "100")),
                timeout=int(os.getenv('BUILD_TIMEOUT', "300")),
                parallel_builds=int(os.getenv('PARALLEL_BUILDS', "1")),
                cleanup_after_build=os.getenv('CLEANUP_AFTER_BUILD', "true").lower() == "true"
            )
        except ValueError as e:
            raise ConfigError(f"Invalid build configuration value: {e}")

@dataclass
class CacheConfig:
    """Cache configuration settings."""
    enabled: bool = True
    directory: str = ".cache"
    ttl: int = 3600  # 1 hour in seconds
    max_size_mb: int = 1000  # 1GB
    
    @classmethod
    def from_env(cls) -> 'CacheConfig':
        """Create cache config from environment variables."""
        try:
            return cls(
                enabled=os.getenv('CACHE_ENABLED', "true").lower() == "true",
                directory=os.getenv('CACHE_DIR', ".cache"),
                ttl=int(os.getenv('CACHE_TTL', "3600")),
                max_size_mb=int(os.getenv('CACHE_MAX_SIZE_MB', "1000"))
            )
        except ValueError as e:
            raise ConfigError(f"Invalid cache configuration value: {e}")

@dataclass
class LoggingConfig:
    """Logging configuration settings."""
    level: str = "INFO"
    file: Optional[str] = None
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    @classmethod
    def from_env(cls) -> 'LoggingConfig':
        """Create logging config from environment variables."""
        return cls(
            level=os.getenv('LOG_LEVEL', "INFO"),
            file=os.getenv('LOG_FILE'),
            format=os.getenv('LOG_FORMAT', "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )

@dataclass
class Config:
    """Main configuration class."""
    api: APIConfig
    build: BuildConfig
    cache: CacheConfig
    logging: LoggingConfig
    
    @classmethod
    def load(cls, env_file: Optional[str] = None) -> 'Config':
        """
        Load configuration from environment variables and optional .env file.
        
        Args:
            env_file: Optional path to .env file
            
        Returns:
            Config: Configuration object
            
        Raises:
            ConfigError: If required configuration is missing or invalid
        """
        try:
            # Load environment variables
            if env_file:
                if not os.path.exists(env_file):
                    raise ConfigError(f"Environment file not found: {env_file}")
                load_dotenv(env_file)
            
            # Create configuration objects
            return cls(
                api=APIConfig.from_env(),
                build=BuildConfig.from_env(),
                cache=CacheConfig.from_env(),
                logging=LoggingConfig.from_env()
            )
            
        except Exception as e:
            raise ConfigError(f"Failed to load configuration: {e}")
    
    @classmethod
    def from_env(cls) -> 'Config':
        """
        Create configuration from environment variables.
        
        This method attempts to load from .env file in the current directory
        if it exists, then falls back to environment variables.
        """
        env_file = ".env"
        if os.path.exists(env_file):
            return cls.load(env_file)
        return cls.load()
    
    def setup_logging(self):
        """Configure logging based on settings."""
        try:
            # Set up logging configuration
            logging_config = {
                'level': getattr(logging, self.logging.level.upper()),
                'format': self.logging.format
            }
            
            # Add file handler
            if self.logging.file:
                log_dir = os.path.dirname(self.logging.file)
                if log_dir:
                    os.makedirs(log_dir, exist_ok=True)
                logging_config['filename'] = self.logging.file
            
            logging.basicConfig(**logging_config)
            
        except Exception as e:
            raise ConfigError(f"Failed to configure logging: {e}")
    
    def validate(self):
        """
        Validate configuration settings.
        
        Raises:
            ConfigError: If configuration is invalid
        """
        try:
            # Validate API
            if not self.api.openai_api_key or not self.api.github_api_key:
                raise ConfigError("API keys are required")
            
            if self.build.max_results < 1:
                raise ConfigError("max_results must be positive")
            if self.build.min_stars < 0:
                raise ConfigError("min_stars cannot be negative")
            if self.build.timeout < 0:
                raise ConfigError("timeout cannot be negative")

            if self.cache.enabled:
                if self.cache.ttl < 0:
                    raise ConfigError("cache_ttl cannot be negative")
                if self.cache.max_size_mb < 1:
                    raise ConfigError("cache_max_size_mb must be positive")
            
            # Create directories
            os.makedirs(self.build.base_download_dir, exist_ok=True)
            if self.cache.enabled:
                os.makedirs(self.cache.directory, exist_ok=True)
                
        except Exception as e:
            raise ConfigError(f"Configuration validation failed: {e}") 
