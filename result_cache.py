"""
Cache management for GitHub Analyzer.
Handles caching of analysis results and repository data.
"""

import os
import json
import aiofiles
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from settings import Config
from exceptions import CacheError
from models import Repository

class CacheManager:
    """Manages caching of repository analysis results."""
    
    def __init__(self, cache_dir: str = ".cache", cache_ttl: int = 3600):
        """
        Initialize cache manager.
        
        Args:
            cache_dir: Directory to store cache files
            cache_ttl: Cache time-to-live in seconds (default: 1 hour)
        """
        self.cache_dir = cache_dir
        self.cache_ttl = cache_ttl
        self.memory_cache: Dict[str, Any] = {}
        self._setup_cache_dir()
    
    def _setup_cache_dir(self):
        """Create cache directory if it doesn't exist."""
        try:
            os.makedirs(self.cache_dir, exist_ok=True)
            os.makedirs(os.path.join(self.cache_dir, 'repositories'), exist_ok=True)
            os.makedirs(os.path.join(self.cache_dir, 'analysis'), exist_ok=True)
        except Exception as e:
            raise CacheError(f"Failed to setup cache directory: {e}")
    
    async def get_cached_result(self, key: str, category: str = 'repositories') -> Optional[Dict]:
        """
        Retrieve cached result.
        
        Args:
            key: Cache key (usually repository full name)
            category: Cache category ('repositories' or 'analysis')
            
        Returns:
            Optional[Dict]: Cached data if exists and valid, None otherwise
        """
        try:
            # Check memory cache first
            memory_key = f"{category}:{key}"
            if memory_key in self.memory_cache:
                return self.memory_cache[memory_key]
            
            # Check file cache
            cache_file = os.path.join(self.cache_dir, category, f"{key}.json")
            if not os.path.exists(cache_file):
                return None
                
            # Check if cache is expired
            if self._is_cache_expired(cache_file):
                await self.invalidate_cache(key, category)
                return None
            
            # Read and return cache
            async with aiofiles.open(cache_file, 'r') as f:
                data = json.loads(await f.read())
                self.memory_cache[memory_key] = data
                return data
                
        except Exception as e:
            raise CacheError(f"Failed to retrieve cache: {e}")
    
    async def cache_result(self, key: str, data: Dict, category: str = 'repositories'):
        """
        Cache analysis result.
        
        Args:
            key: Cache key
            data: Data to cache
            category: Cache category
        """
        try:
            # Add timestamp
            data['_cached_at'] = datetime.utcnow().isoformat()
            
            # Update memory cache
            memory_key = f"{category}:{key}"
            self.memory_cache[memory_key] = data
            
            # Write to file cache
            cache_file = os.path.join(self.cache_dir, category, f"{key}.json")
            async with aiofiles.open(cache_file, 'w') as f:
                await f.write(json.dumps(data, indent=2))
                
        except Exception as e:
            raise CacheError(f"Failed to cache result: {e}")
    
    async def invalidate_cache(self, key: str, category: str = 'repositories'):
        """Invalidate cache for given key."""
        try:
            # Remove from memory cache
            memory_key = f"{category}:{key}"
            self.memory_cache.pop(memory_key, None)
            
            # Remove file cache
            cache_file = os.path.join(self.cache_dir, category, f"{key}.json")
            if os.path.exists(cache_file):
                os.remove(cache_file)
                
        except Exception as e:
            raise CacheError(f"Failed to invalidate cache: {e}")
    
    def _is_cache_expired(self, cache_file: str) -> bool:
        """Check if cache file is expired."""
        try:
            with open(cache_file, 'r') as f:
                data = json.loads(f.read())
                cached_at = datetime.fromisoformat(data['_cached_at'])
                return (datetime.utcnow() - cached_at) > timedelta(seconds=self.cache_ttl)
        except Exception:
            return True
    
    async def clear_cache(self):
        """Clear all cache data."""
        try:
            # Clear memory cache
            self.memory_cache.clear()
            
            # Clear file cache
            for category in ['repositories', 'analysis']:
                cache_dir = os.path.join(self.cache_dir, category)
                for file in os.listdir(cache_dir):
                    os.remove(os.path.join(cache_dir, file))
                    
        except Exception as e:
            raise CacheError(f"Failed to clear cache: {e}") 