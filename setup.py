"""
Setup configuration for GitHub Repository Analyzer
"""

from setuptools import setup, find_packages
from __init__ import __version__

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="github-analyzer",
    version=__version__,
    py_modules=[
        'main_analyzer',
        'repo_analyzer',
        'project_builder',
        'query_processor',
        'result_cache',
        'settings',
        'models',
        'exceptions',
        'user_interaction'
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="AI-powered GitHub repository search and analysis tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/github-analyzer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=[
        "dspy-ai>=1.0.0",
        "openai>=1.0.0",
        "PyGithub>=2.1.1",
        "langchain>=0.0.300",
        "aiofiles>=23.1.0",
        "rich>=13.0.0",
        "GitPython>=3.1.0",
        "python-dotenv>=1.0.0"
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-asyncio>=0.21.0',
            'pytest-cov>=4.0.0',
            'black>=23.0.0',
            'isort>=5.12.0',
            'mypy>=1.0.0',
            'flake8>=6.0.0',
        ]
    },
    entry_points={
        'console_scripts': [
            'github-analyzer=__main__:main',
        ],
    },
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/github-analyzer/issues",
        "Documentation": "https://github.com/yourusername/github-analyzer/wiki",
        "Source Code": "https://github.com/yourusername/github-analyzer",
    },
) 