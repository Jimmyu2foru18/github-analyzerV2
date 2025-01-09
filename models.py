"""Data models for GitHub repository analysis."""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime

@dataclass
class SearchCriteria:
    """Search criteria for repository queries."""
    query: str
    language: Optional[str] = None
    topics: List[str] = None
    min_stars: int = 0

@dataclass
class Repository:
    """Repository information and analysis results."""
    name: str
    full_name: str
    description: str
    stars: int
    url: str
    topics: List[str]
    last_updated: datetime
    relevance_score: Optional[float] = None
    readme_analysis: Optional[Dict[str, Any]] = None
    code_similarity_score: Optional[float] = None

@dataclass
class BuildInstructions:
    """Build instructions for a repository."""
    language: str
    build_system: str
    dependencies: List[str]
    setup_steps: List[str]
    build_commands: List[str]
    test_commands: List[str]

@dataclass
class UserChoice:
    """User interaction choice."""
    action: str  # "download", "refine", "exit"
    repository: Optional[Repository] = None 