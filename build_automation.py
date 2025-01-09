"""
Build///Automation Component
-------------------------
This part does the repository build processes
- Repository downloading
- Build system detection
- Dependency analysis
- Build execution
"""

import logging
import os
import shutil
import subprocess
import asyncio
from typing import List, Dict, Optional
from pathlib import Path
import tempfile
from git import Repo
import toml

from config import Config
from models import Repository, BuildInstructions
from exceptions import BuildError

logger = logging.getLogger(__name__)

class BuildAutomation:
    """Handles repository build and automation."""
    
    def __init__(self, config: Config):
        """Initialize build automation."""
        self.config = config
        self.build_handlers = {
            'python': self._handle_python_build,
            'javascript': self._handle_javascript_build,
            'typescript': self._handle_javascript_build,
            'java': self._handle_java_build,
            'go': self._handle_go_build,
            'rust': self._handle_rust_build
        }
    
    async def download_repository(self, repository: Repository) -> str:
        """
        Download repository to local directory.
        
        Args:
            repository: Repository to download
            
        Returns:
            str: Path to downloaded repository
        """
        try:
            # Create temporary directory
            repo_dir = os.path.join(self.config.build.base_download_dir, repository.name)
            os.makedirs(repo_dir, exist_ok=True)
            
            # Clone repository
            Repo.clone_from(repository.url, repo_dir)
            
            return repo_dir
            
        except Exception as e:
            logger.error(f"Repository download failed: {e}")
            raise BuildError(f"Download failed: {e}")
    
    async def detect_build_instructions(self, repo_path: str) -> BuildInstructions:
        """
        Detect build instructions for repository.
        
        Args:
            repo_path: Path to repository
            
        Returns:
            BuildInstructions: Detected build instructions
        """
        try:
            # Detect primary language
            language = await self._detect_primary_language(repo_path)
            
            # Detect build system
            build_system = await self._detect_build_system(repo_path, language)
            
            # Analyze dependencies
            dependencies = await self._analyze_dependencies(repo_path, language)
            
            # Create build steps
            setup_steps = await self._create_setup_steps(language, build_system)
            build_commands = await self._create_build_commands(language, build_system)
            test_commands = await self._create_test_commands(language, build_system)
            
            return BuildInstructions(
                language=language,
                build_system=build_system,
                dependencies=dependencies,
                setup_steps=setup_steps,
                build_commands=build_commands,
                test_commands=test_commands
            )
            
        except Exception as e:
            logger.error(f"Build instruction detection failed: {e}")
            raise BuildError(f"Detection failed: {e}")
    
    async def execute_build(self, repo_path: str, instructions: BuildInstructions) -> bool:
        """Execute build process."""
        try:
            # Setup build environment
            await self._setup_environment(repo_path, instructions)
            
            # Execute build handler for specific language
            handler = self.build_handlers.get(instructions.language.lower())
            if handler:
                return await handler(repo_path, instructions)
            else:
                raise BuildError(f"Unsupported language: {instructions.language}")
                
        except subprocess.CalledProcessError as e:
            logger.error(f"Build execution failed: {e}")
            # Implements the retry logic here
            return await self._handle_build_failure(repo_path, e)
    
    async def _detect_primary_language(self, repo_path: str) -> str:
        """Detect primary programming language."""
        language_patterns = {
            'python': ['*.py', 'requirements.txt', 'setup.py', 'pyproject.toml'],
            'javascript': ['*.js', 'package.json'],
            'typescript': ['*.ts', 'tsconfig.json'],
            'java': ['*.java', 'pom.xml', 'build.gradle'],
            'go': ['*.go', 'go.mod'],
            'rust': ['*.rs', 'Cargo.toml']
        }
        
        # Count files for each language
        counts = {}
        for lang, patterns in language_patterns.items():
            count = 0
            for pattern in patterns:
                count += len(list(Path(repo_path).rglob(pattern)))
            counts[lang] = count
        
        # Return language with most files
        return max(counts.items(), key=lambda x: x[1])[0]
    
    async def _detect_build_system(self, repo_path: str, language: str) -> str:
        """Detect build system based on language and files."""
        build_systems = {
            'python': {
                'setup.py': 'setuptools',
                'pyproject.toml': 'poetry',
                'requirements.txt': 'pip'
            },
            'javascript': {
                'package.json': 'npm',
                'yarn.lock': 'yarn'
            },
            'java': {
                'pom.xml': 'maven',
                'build.gradle': 'gradle'
            },
            'go': {
                'go.mod': 'go'
            },
            'rust': {
                'Cargo.toml': 'cargo'
            }
        }
        
        if language in build_systems:
            for file, system in build_systems[language].items():
                if os.path.exists(os.path.join(repo_path, file)):
                    return system
        
        return 'unknown'
    
    async def _analyze_dependencies(self, repo_path: str, language: str) -> List[str]:
        """Analyze project dependencies."""
        analyzers = {
            'python': self._analyze_python_dependencies,
            'javascript': self._analyze_javascript_dependencies,
            'java': self._analyze_java_dependencies,
            'go': self._analyze_go_dependencies,
            'rust': self._analyze_rust_dependencies
        }
        
        analyzer = analyzers.get(language)
        if analyzer:
            return await analyzer(repo_path)
        return []
    
    # Language-specific
    async def _handle_python_build(self, repo_path: str, instructions: BuildInstructions) -> bool:
        """Handle Python project build."""
        try:
            # Setup vm
            venv_path = os.path.join(repo_path, '.venv')
            subprocess.run(['python', '-m', 'venv', venv_path], check=True)
            
            # Install dependents
            pip = os.path.join(venv_path, 'bin', 'pip')
            for cmd in instructions.build_commands:
                subprocess.run([pip] + cmd.split(), check=True)
            
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Python build failed: {e}")
            return False
    
    async def _handle_javascript_build(self, repo_path: str, instructions: BuildInstructions) -> bool:
        """Handle JavaScript/TypeScript project build."""
        try:
            # Install dependents
            subprocess.run(['npm', 'install'], cwd=repo_path, check=True)
            
            # Execute build
            for cmd in instructions.build_commands:
                subprocess.run(cmd.split(), cwd=repo_path, check=True)
            
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"JavaScript build failed: {e}")
            return False
    
    # analysis methods
    async def _analyze_python_dependencies(self, repo_path: str) -> List[str]:
        """Analyze Python project dependencies."""
        dependencies = []
        
        try:
            # Check requirements.txt
            req_file = os.path.join(repo_path, 'requirements.txt')
            if os.path.exists(req_file):
                with open(req_file) as f:
                    dependencies.extend(line.strip() for line in f if line.strip())
            
            # Check setup.py
            setup_file = os.path.join(repo_path, 'setup.py')
            if os.path.exists(setup_file):
                # Parse setup.py for install_requires
                with open(setup_file) as f:
                    content = f.read()
                    if 'install_requires' in content:
                        # Extracts
                        pass
            
            return dependencies
            
        except Exception as e:
            logger.error(f"Failed to analyze Python dependencies: {e}")
            return []
    
    async def _analyze_javascript_dependencies(self, repo_path: str) -> List[str]:
        """Analyze JavaScript project dependencies."""
        dependencies = []
        
        try:
            package_file = os.path.join(repo_path, 'package.json')
            if os.path.exists(package_file):
                with open(package_file) as f:
                    import json
                    data = json.load(f)
                    deps = data.get('dependencies', {})
                    dev_deps = data.get('devDependencies', {})
                    dependencies.extend(f"{name}@{version}" for name, version in deps.items())
                    dependencies.extend(f"{name}@{version}" for name, version in dev_deps.items())
            
            return dependencies
            
        except Exception as e:
            logger.error(f"Failed to analyze JavaScript dependencies: {e}")
            return []
    
    async def _analyze_go_dependencies(self, repo_path: str) -> List[str]:
        """Analyze Go project dependencies."""
        dependencies = []
        
        try:
            # Parse go.mod file
            go_mod = os.path.join(repo_path, 'go.mod')
            if os.path.exists(go_mod):
                with open(go_mod) as f:
                    content = f.read()
                    # Extract require block
                    if 'require (' in content:
                        require_block = content.split('require (')[1].split(')')[0]
                        for line in require_block.splitlines():
                            if line.strip():
                                dependencies.append(line.strip())
            
            return dependencies
            
        except Exception as e:
            logger.error(f"Failed to analyze Go dependencies: {e}")
            return []
    
    async def _analyze_rust_dependencies(self, repo_path: str) -> List[str]:
        """Analyze Rust project dependencies."""
        dependencies = []
        
        try:
            cargo_toml = os.path.join(repo_path, 'Cargo.toml')
            if os.path.exists(cargo_toml):
                with open(cargo_toml) as f:
                    cargo_data = toml.load(f)
                    if 'dependencies' in cargo_data:
                        for name, version in cargo_data['dependencies'].items():
                            if isinstance(version, str):
                                dependencies.append(f"{name} = {version}")
                            elif isinstance(version, dict):
                                dependencies.append(f"{name} = {version.get('version', '*')}")
            
            return dependencies
            
        except Exception as e:
            logger.error(f"Failed to analyze Rust dependencies: {e}")
            return []
    
    async def _handle_build_failure(self, repo_path: str, error: Exception) -> bool:
        """Handle build failures with retry logic."""
        try:
            # Clean build
            await self._clean_build_artifacts(repo_path)
            
            # Retry build
            modified_instructions = await self._modify_build_instructions(repo_path)
            return await self.execute_build(repo_path, modified_instructions)
            
        except Exception as retry_error:
            logger.error(f"Build retry failed: {retry_error}")
            return False
    
    async def _clean_build_artifacts(self, repo_path: str):
        """Clean build artifacts before retry."""
        try:
            # Common builds to try
            build_dirs = ['build', 'dist', 'target', 'node_modules', '__pycache__']
            for dir_name in build_dirs:
                dir_path = os.path.join(repo_path, dir_name)
                if os.path.exists(dir_path):
                    shutil.rmtree(dir_path)
        except Exception as e:
            logger.warning(f"Failed to clean build artifacts: {e}")
    
    async def _modify_build_instructions(self, repo_path: str) -> BuildInstructions:
        """
        Modify build instructions for retry attempt.
        
        This method analyzes build failures and adjusts instructions accordingly.
        """
        try:
            # Detect language the builds it 
            language = await self._detect_primary_language(repo_path)
            build_system = await self._detect_build_system(repo_path, language)
            
            # Get info with constraints
            dependencies = await self._analyze_dependencies(repo_path, language)
            dependencies = [d.replace('==', '>=') for d in dependencies]
            
            # Create the process with modified build steps
            setup_steps = [
                "Clean build artifacts",
                "Update package manager",
                "Install dependencies with relaxed constraints"
            ]
            
            build_commands = []
            if language == 'python':
                build_commands = [
                    "pip install --upgrade pip",
                    "pip install -r requirements.txt --upgrade"
                ]
            elif language in ['javascript', 'typescript']:
                build_commands = [
                    "npm cache clean --force",
                    "npm install --no-package-lock"
                ]
            
            return BuildInstructions(
                language=language,
                build_system=build_system,
                dependencies=dependencies,
                setup_steps=setup_steps,
                build_commands=build_commands,
                test_commands=[]  # Skip test
            )
            
        except Exception as e:
            logger.error(f"Failed to modify build instructions: {e}")
            raise BuildError(f"Could not modify build instructions: {e}")
    
    async def _setup_environment(self, repo_path: str, instructions: BuildInstructions):
        """Setup build environment."""
        try:
            # Create vm -python 
            if instructions.language.lower() == 'python':
                venv_path = os.path.join(repo_path, '.venv')
                if not os.path.exists(venv_path):
                    subprocess.run(['python', '-m', 'venv', venv_path], check=True)
            
            # Setup Node.js
            elif instructions.language.lower() in ['javascript', 'typescript']:
                if not os.path.exists(os.path.join(repo_path, 'node_modules')):
                    subprocess.run(['npm', 'install'], cwd=repo_path, check=True)
                
        except Exception as e:
            logger.error(f"Environment setup failed: {e}")
            raise BuildError(f"Failed to setup environment: {e}")

    async def _handle_java_build(self, repo_path: str, instructions: BuildInstructions) -> bool:
        """Handle Java project build."""
        pass

    async def _handle_go_build(self, repo_path: str, instructions: BuildInstructions) -> bool:
        """Handle Go project build."""
        pass

    async def _handle_rust_build(self, repo_path: str, instructions: BuildInstructions) -> bool:
        """Handle Rust project build."""
        pass

    async def _create_setup_steps(self, language: str, build_system: str) -> List[str]:
        """Create setup steps based on language and build system."""
        pass

    async def _create_build_commands(self, language: str, build_system: str) -> List[str]:
        """Create build commands based on language and build system."""
        pass

    async def _create_test_commands(self, language: str, build_system: str) -> List[str]:
        """Create test commands based on language and build system."""
        pass

    async def _analyze_java_dependencies(self, repo_path: str) -> List[str]:
        """Analyze Java project dependencies."""
        pass
