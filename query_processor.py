"""
Chain of Thought Component
-------------------------

This component implements double chain of thought reasoning for query 
using DSPy.
"""

import logging
from typing import Dict, Any, List, Optional
import dspy
from settings import Config
from exceptions import AnalysisError

logger = logging.getLogger(__name__)

class QueryAnalyzer(dspy.Module):
    """DSPy module for primary query analysis."""
    
    def __init__(self):
        super().__init__()
        self.analyze = dspy.Predict('query -> components, context, requirements')
    
    def forward(self, query: str) -> Dict[str, Any]:
        """
        Analyze query using primary chain of thought.
        
        Args:
            query: User's search query
            
        Returns:
            Dict containing analysis results
        """
        result = self.analyze(
            query=query,
            prompt="""
            Analyze this GitHub repository search query in detail:
            1. Extract key technical components and requirements
            2. Identify implicit technical context
            3. Determine specific constraints or preferences
            4. Note related technologies or frameworks
            5. Consider potential use cases
            
            Format the response as:
            {
                "components": {
                    "keywords": [...],
                    "technologies": [...],
                    "frameworks": [...]
                },
                "context": {
                    "domain": "...",
                    "purpose": "...",
                    "relevant_terms": [...]
                },
                "requirements": {
                    "explicit": [...],
                    "implicit": [...],
                    "constraints": [...]
                }
            }
            """
        )
        return result

class MetaAnalyzer(dspy.Module):
    """DSPy module for secondary (meta) analysis."""
    
    def __init__(self):
        super().__init__()
        self.meta_analyze = dspy.Predict('analysis -> validation, suggestions, concerns')
    
    def forward(self, primary_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform meta-analysis on primary results.
        
        Args:
            primary_analysis: Results from primary analysis
            
        Returns:
            Dict containing meta-analysis results
        """
        result = self.meta_analyze(
            analysis=primary_analysis,
            prompt="""
            Perform meta-analysis on the search parameters:
            1. Validate logical consistency of components
            2. Identify potential gaps or missing contexts
            3. Suggest additional relevant terms or concepts
            4. Note potential ambiguities or conflicts
            5. Consider edge cases and limitations
            
            Format the response as:
            {
                "validation": {
                    "consistent": bool,
                    "issues": [...]
                },
                "suggestions": [...],
                "concerns": {
                    "ambiguities": [...],
                    "missing_context": [...],
                    "limitations": [...]
                }
            }
            """
        )
        return result

class ChainOfThought:
    """
    Implements double chain of thought reasoning for query analysis.
    
    This class uses DSPy to implement a sophisticated reasoning system that:
    1. Analyzes user queries for intent and requirements
    2. Performs meta-analysis to validate and improve understanding
    3. Refines search parameters based on combined analysis
    """
    
    def __init__(self, config: Config):
        """Initialize the chain of thought processor."""
        self.config = config
        self._setup_dspy()
        
    def _setup_dspy(self):
        """Setup DSPy modules and configuration."""
        try:
            # Configure DSPy with OpenAI
            dspy.settings.configure(
                lm=dspy.OpenAI(
                    api_key=self.config.api.openai_api_key,
                    model=self.config.api.model_name
                )
            )
            
            # Initialize analyzers
            self.primary_analyzer = QueryAnalyzer()
            self.meta_analyzer = MetaAnalyzer()
            
        except Exception as e:
            logger.error(f"Failed to setup DSPy: {e}")
            raise AnalysisError(f"DSPy setup failed: {e}")
    
    async def analyze_query(self, query: str) -> Dict[str, Any]:
        """
        Analyze user query using double chain of thought.
        
        Args:
            query: User's search query
            
        Returns:
            Dict containing analysis results
            
        Raises:
            AnalysisError: If analysis fails
        """
        try:
            # Primary analysis
            primary_result = await self.primary_analyzer(query)
            
            # Meta analysis
            secondary_result = await self.meta_analyzer(primary_result)
            
            # Combine and refine results
            final_result = self._combine_analysis(primary_result, secondary_result)
            
            return final_result
            
        except Exception as e:
            logger.error(f"Query analysis failed: {e}")
            raise AnalysisError(f"Analysis failed: {e}")
    
    def _combine_analysis(
        self, 
        primary: Dict[str, Any], 
        secondary: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Combine and reconcile results from both chains."""
        return {
            "components": primary.get("components", {}),
            "context": primary.get("context", {}),
            "requirements": primary.get("requirements", {}),
            "meta_analysis": secondary,
            "refined_query": self._build_refined_query(primary, secondary)
        }
    
    def _build_refined_query(
        self, 
        primary: Dict[str, Any], 
        secondary: Dict[str, Any]
    ) -> str:
        """Build refined query from combined analysis."""
        query_components = []
        
        # Add primary components
        if "components" in primary:
            query_components.extend(primary["components"].get("keywords", []))
            query_components.extend(primary["components"].get("technologies", []))
            
        # Add context-specific terms
        if "context" in primary:
            query_components.extend(primary["context"].get("relevant_terms", []))
            
        # Apply refinements from secondary analysis
        if "suggestions" in secondary:
            # Filter and add relevant suggestions
            suggestions = [
                s for s in secondary["suggestions"]
                if not any(s.lower() in q.lower() for q in query_components)
            ]
            query_components.extend(suggestions[:2])  # Limit to top 2 suggestions
            
        # Build final query string
        query = " ".join(query_components)
        
        # Add any necessary qualifiers
        if "requirements" in primary:
            constraints = primary["requirements"].get("constraints", [])
            if constraints:
                query += f" {' '.join(constraints)}"
                
        return query.strip() 
