"""Custom exceptions for the GitHub analyzer."""

class GitHubAnalyzerError(Exception):
    """Base exception for GitHub analyzer errors."""
    pass

class ConfigError(GitHubAnalyzerError):
    """Raised when configuration is invalid or missing."""
    pass

class APIError(GitHubAnalyzerError):
    """Raised when API requests fail."""
    pass

class AnalysisError(GitHubAnalyzerError):
    """Raised when repository analysis fails."""
    pass

class BuildError(GitHubAnalyzerError):
    """Raised when repository build fails."""
    pass

class CacheError(GitHubAnalyzerError):
    """Raised when cache operations fail."""
    pass 