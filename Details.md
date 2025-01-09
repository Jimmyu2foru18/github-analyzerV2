# GitHub Repository Analyzer

An AI-powered tool for searching, analyzing, and building GitHub repositories.

## Features

- Intelligent search query analysis using Chain of Thought reasoning
- Repository relevance scoring
- Code similarity analysis
- README content analysis
- Multi-language build automation
- Caching system for improved performance

## Components

1. **GitHub Analyzer**
   - Main coordination component
   - Handles user interaction
   - Manages analysis workflow

2. **Repository Analyzer**
   - GitHub API integration
   - Repository searching
   - Content analysis
   - Relevance scoring

3. **Build Automation**
   - Repository downloading
   - Build system detection
   - Dependency management
   - Build execution

4. **Chain of Thought**
   - Query analysis
   - Context understanding
   - Search refinement

5. **Cache Manager**
   - Result caching
   - Performance optimization
   - Cache invalidation

## Configuration

See `.env.example` for required configuration settings.

## Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Run the analyzer
python -m github_analyzer
```

## Development

- Python 3.9+
- Uses asyncio for concurrent operations
- OpenAI API for content analysis
- GitHub API for repository access 