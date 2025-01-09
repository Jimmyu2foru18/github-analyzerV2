"""User interaction component."""

import logging
from typing import List
from rich.console import Console
from rich.table import Table
from models import Repository, UserChoice

logger = logging.getLogger(__name__)
console = Console()

class UserInteraction:
    """Handles user interaction."""
    
    async def get_search_query(self) -> str:
        """Get search query from user."""
        console.print("\nEnter your search query:")
        return console.input("> ").strip()
    
    async def present_options(self, repositories: List[Repository]) -> UserChoice:
        """Present repository options to user."""
        table = Table(title="Found Repositories")
        
        # Add columns
        table.add_column("Index", justify="right", style="cyan")
        table.add_column("Repository", style="green")
        table.add_column("Description")
        table.add_column("Stars", justify="right")
        table.add_column("Score", justify="right")
        
        # Add rows
        for i, repo in enumerate(repositories, 1):
            table.add_row(
                str(i),
                repo.full_name,
                repo.description[:100] + "..." if repo.description else "",
                str(repo.stars),
                f"{repo.relevance_score:.2f}" if repo.relevance_score else "N/A"
            )
        
        console.print(table)
        console.print("\nOptions:")
        console.print("1-N: Download repository")
        console.print("r: Refine search")
        console.print("q: Quit")
        
        while True:
            choice = console.input("\nEnter your choice: ").strip().lower()
            
            if choice == 'q':
                return UserChoice(action="exit")
            elif choice == 'r':
                return UserChoice(action="refine")
            elif choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(repositories):
                    return UserChoice(
                        action="download",
                        repository=repositories[idx]
                    )
            
            console.print("[red]Invalid choice. Please try again.[/]") 
