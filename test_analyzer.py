import pytest
from github_analyzer import GitHubAnalyzer

@pytest.mark.asyncio
async def test_search_and_analyze():
    analyzer = GitHubAnalyzer()
    results = await analyzer.search_and_analyze("test query")
    assert len(results) > 0
    assert all(hasattr(r, 'relevance_score') for r in results) 