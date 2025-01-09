# GitHub Repository Analyzer

An AI-powered tool for intelligent GitHub repository search, analysis, and build automation.

## Features

- 🔍 **Intelligent Search**: Uses AI to understand and refine search queries
- 📊 **Repository Analysis**: 
  - Code similarity detection
  - README content analysis
  - Relevance scoring
  - Dependency analysis
- 🛠️ **Build Automation**:
  - Multi-language support (Python, JavaScript, Java, Go, Rust)
  - Automatic build system detection
  - Dependency management
  - Build verification
- 🧠 **AI Integration**:
  - OpenAI GPT-4 powered analysis
  - Chain of thought reasoning
  - Context-aware search refinement
- 💾 **Caching System**:
  - Efficient result caching
  - Configurable TTL
  - Memory and file-based caching

## Installation

```bash
# Clone the repository
git clone https://github.com/jimmyu2foru18/github-analyzerV2.git
cd github-analyzer

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys and settings
```

## Configuration

Required environment variables:
```env
OPENAI_API_KEY=your_openai_api_key
GITHUB_API_KEY=your_github_api_key
```

Optional settings:
```env
# Cache Settings
CACHE_ENABLED=true
CACHE_TTL=3600
CACHE_DIR=.cache

# Build Settings
BUILD_DOWNLOAD_DIR=downloads
MAX_RESULTS=5
MIN_STARS=100
BUILD_TIMEOUT=300
```

## Usage

```bash
# Run the interactive analyzer
python -m github_analyzer

# Or use as a library
from main_analyzer import GitHubAnalyzer

analyzer = GitHubAnalyzer()
results = await analyzer.search_and_analyze("machine learning framework python")
```

## Project Structure

```
github-analyzer/
├── main_analyzer.py      # Main coordination component
├── repo_analyzer.py      # Repository analysis
├── project_builder.py    # Build automation
├── query_processor.py    # Query analysis
├── result_cache.py       # Caching system
├── settings.py          # Configuration
├── models.py            # Data models
├── exceptions.py        # Custom exceptions
└── user_interaction.py  # CLI interface
```

## Development

Requirements:
- Python 3.9+
- OpenAI API key
- GitHub API key

Setup development environment:
```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
flake8
black .
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- OpenAI for GPT-4 API
- GitHub for their API
- DSPy for chain of thought implementation
