"""
Main Analyzer Component
----------------------

Main coordination component for GitHub repository analysis.
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional

from result_cache import CacheManager
from settings import Config
from models import Repository, SearchCriteria
from exceptions import GitHubAnalyzerError
from repo_analyzer import RepositoryAnalyzer
from project_builder import BuildAutomation
from query_processor import ChainOfThought
from user_interaction import UserInteraction

logger = logging.getLogger(__name__)

class GitHubAnalyzer:
    """Main class coordinating repository analysis and build processes."""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config.from_env()
        self.cache_manager = CacheManager()
        self.setup_components()
