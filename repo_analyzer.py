"""
Repository Analyzer Component
---------------------------
This handles GitHub repository searching, analysis, and scoring.
It analyzes repository content, 
README files, 
and metadata to determine relevance
to the user's search query.
"""

import logging
import base64
import tempfile
import os
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
from github import Github, Repository as GithubRepo
from github.GithubException import GithubException
import asyncio
from git import Repo

from settings import Config
from models import Repository, SearchCriteria
from exceptions import APIError, AnalysisError

logger = logging.getLogger(__name__)

class RepositoryAnalyzer:
    """
    Analyzes GitHub repositories for relevance and content.
    
    This class handles:
    1. Repository searching using GitHub API
    2. README content analysis
    3. Repository metadata evaluation
    4. Relevance scoring
    """
    
    def __init__(self, config: Config):
        """Initialize the repository analyzer."""
        self.config = config
        self.github_client = Github(config.api.github_api_key)
        self._setup_analyzers()
    
    def _setup_analyzers(self):
        """Initialize analysis components."""
        try:
            # Setup OpenAI for content analysis
            import openai
            openai.api_key = self.config.api.openai_api_key
            self.openai_client = openai.Client()
        except Exception as e:
            logger.error(f"Failed to setup analyzers: {e}")
            raise AnalysisError(f"Analyzer setup failed: {e}")
    
    async def search(self, criteria: SearchCriteria) -> List[Repository]:
        """
        Search for repositories matching.
        
        Args:
            criteria: Search criteria
            
        Returns:
            List[Repository]: Matching repositories
            
        Raises:
            APIError: If GitHub API request fails
        """
        try:
            # Build search query
            query = criteria.query
            if criteria.language:
                query += f" language:{criteria.language}"
            if criteria.min_stars:
                query += f" stars:>={criteria.min_stars}"
            
            # Add topic filters
            if criteria.topics:
                for topic in criteria.topics:
                    query += f" topic:{topic}"
            
            # Execute search
            repositories = self.github_client.search_repositories(
                query=query,
                sort="stars",
                order="desc"
            )
            
            # Convert to internal Repository objects
            results = []
            for repo in repositories[:self.config.build.max_results]:
                results.append(
                    Repository(
                        name=repo.name,
                        full_name=repo.full_name,
                        description=repo.description or "",
                        stars=repo.stargazers_count,
                        url=repo.clone_url,
                        topics=repo.get_topics(),
                        last_updated=repo.updated_at,
                        relevance_score=None,
                        readme_analysis=None
                    )
                )
            
            return results
            
        except GithubException as e:
            logger.error(f"GitHub API error: {e}")
            raise APIError(f"GitHub search failed: {e}")
        except Exception as e:
            logger.error(f"Search error: {e}")
            raise AnalysisError(f"Repository search failed: {e}")
    
    async def analyze_repository(self, repository: Repository) -> Repository:
        """
        Perform detailed analysis of a repository.
        
        Args:
            repository: Repository to analyze
            
        Returns:
            Repository: Analyzed repository with scores
        """
        try:
            # Get repository details from GitHub
            repo = self.github_client.get_repo(repository.full_name)
            
            # Analyze README content
            readme_analysis = await self._analyze_readme(repo)
            
            # Calculate code similarity score
            similarity_score = await self.analyze_code_similarity(repository)
            
            # Calculate relevance score
            relevance_score = self._calculate_relevance_score(
                repository,
                readme_analysis,
                similarity_score
            )
            
            # Update repository with analysis results
            repository.readme_analysis = readme_analysis
            repository.relevance_score = relevance_score
            repository.code_similarity_score = similarity_score
            
            return repository
            
        except Exception as e:
            logger.error(f"Repository analysis failed: {e}")
            raise AnalysisError(f"Analysis failed for {repository.full_name}: {e}")
    
    async def _analyze_readme(self, repo: GithubRepo) -> Dict[str, Any]:
        """Analyze repository README content."""
        try:
            # Get README content
            try:
                readme = repo.get_readme()
                content = base64.b64decode(readme.content).decode('utf-8')
            except:
                logger.warning(f"No README found for {repo.full_name}")
                return {}
            
            # Read the content with OpenAI
            response = await self.openai_client.chat.completions.create(
                model=self.config.api.model_name,
                messages=[
                    {"role": "system", "content": """
                    Analyze this repository README and extract key information:
                    1. Main purpose and features
                    2. Technologies and frameworks used
                    3. Installation requirements
                    4. Key dependencies
                    5. Project maturity indicators
                    
                    Format the response as JSON with these keys:
                    {
                        "purpose": str,
                        "features": List[str],
                        "technologies": List[str],
                        "requirements": List[str],
                        "dependencies": List[str],
                        "maturity_indicators": Dict[str, Any]
                    }
                    """},
                    {"role": "user", "content": content}
                ]
            )
            
            # Parse and return info...
            import json
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"README analysis failed: {e}")
            return {}
    
    async def analyze_code_similarity(self, repository: Repository) -> float:
        """Analyze code similarity within the repository."""
        try:
            # Clone repository
            with tempfile.TemporaryDirectory() as temp_dir:
                repo_path = os.path.join(temp_dir, repository.name)
                Repo.clone_from(repository.url, repo_path)
                
                # read the code that is similar using tokenization
                similarity_score = await self._calculate_similarity_score(repo_path)
                
                return similarity_score
                
        except Exception as e:
            logger.error(f"Code similarity analysis failed: {e}")
            return 0.0
    
    async def _calculate_similarity_score(self, repo_path: str) -> float:
        """Calculate code similarity score using tokenization."""
        try:
            import tokenize
            from collections import defaultdict
            
            # Store token
            token_frequencies = defaultdict(int)
            duplicate_lines = 0
            total_lines = 0
            
            # Get all source files
            source_files = []
            for ext in ['.py', '.js', '.java', '.go', '.rs']:
                source_files.extend(Path(repo_path).rglob(f'*{ext}'))
            
            # read each file
            for file_path in source_files:
                try:
                    with tokenize.open(file_path) as f:
                        tokens = list(tokenize.generate_tokens(f.readline))
                        
                        # Count lines
                        total_lines += sum(1 for _ in open(file_path))
                        
                        # Create token for similarity of repos
                        token_sequences = [
                            tuple(t.string for t in tokens[i:i+5])
                            for i in range(len(tokens)-4)
                        ]
                        
                        # Count the duplicate 
                        for sequence in token_sequences:
                            if token_frequencies[sequence] > 0:
                                duplicate_lines += 1
                            token_frequencies[sequence] += 1
                            
                except Exception as e:
                    logger.warning(f"Failed to analyze file {file_path}: {e}")
                    continue
            
            # Calculate similarity score
            if total_lines == 0:
                return 0.0
            
            similarity_score = duplicate_lines / total_lines
            return min(1.0, similarity_score)
            
        except Exception as e:
            logger.error(f"Failed to calculate similarity score: {e}")
            return 0.0
    
    def _calculate_relevance_score(
        self,
        repository: Repository,
        readme_analysis: Dict[str, Any],
        similarity_score: float
    ) -> float:
        """Calculate overall repository relevance score."""
        try:
            # Base score from stars
            star_score = min(repository.stars / 10000, 1.0)
            
            # socre the README
            readme_score = len(readme_analysis.get("features", [])) / 10
            readme_score += len(readme_analysis.get("technologies", [])) / 10
            readme_score = min(readme_score, 1.0)
            
            # score for code quality
            code_score = 1.0 - similarity_score
            
            # Calculate averages
            weights = {
                "stars": 0.4,
                "readme": 0.4,
                "code": 0.2
            }
            
            relevance_score = (
                weights["stars"] * star_score +
                weights["readme"] * readme_score +
                weights["code"] * code_score
            )
            
            return round(relevance_score, 3)
            
        except Exception as e:
            logger.error(f"Failed to calculate score: {e}")
            return 0.0
 
