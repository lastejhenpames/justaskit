from openai import OpenAI
from app.core.config import settings
import json
import logging

logger = logging.getLogger(__name__)

class InsightAgent:
    """
    Specialist agent for generating natural language insights
    Synthesizes results from all other agents
    """
    
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL
        )
        self.model = settings.OPENAI_MODEL
    
    def generate_insight(self, query: str, analysis: dict, visualization: dict, cleaning: dict) -> dict:
        """
        Generate natural language insight from all agent results
        
        Returns:
            dict with insight text and confidence
        """
        try:
            # Build context from all agents
            context = self._build_context(query, analysis, visualization, cleaning)
            
            # Generate insight
            insight_text = self._generate_text(context)
            
            # Extract confidence
            confidence = self._calculate_confidence(analysis, visualization)
            
            return {
                "text": insight_text,
                "confidence": confidence,
                "agents_used": self._list_agents_used(analysis, visualization, cleaning)
            }
            
        except Exception as e:
            logger.error(f"Insight generation error: {str(e)}")
            return {
                "text": f"Could not generate insight: {str(e)}",
                "confidence": 0.0,
                "error": str(e)
            }
    
    def _build_context(self, query: str, analysis: dict, visualization: dict, cleaning: dict) -> str:
        """Build context string from all agent outputs"""
        
        context_parts = [f"User Question: {query}\n"]
        
        if cleaning and not cleaning.get("error"):
            report = cleaning.get("report", {})
            if report.get("actions"):
                context_parts.append(f"Data Cleaning: {', '.join(report['actions'])}")
        
        if analysis and not analysis.get("error"):
            result = analysis.get("result")
            context_parts.append(f"Analysis Result: {json.dumps(result, default=str)}")
            context_parts.append(f"Pandas Code: {analysis.get('pandas_code')}")
        
        if visualization and not visualization.get("error"):
            context_parts.append(f"Visualization: {visualization.get('chart_type')} chart created")
        
        return "\n".join(context_parts)
    
    def _generate_text(self, context: str) -> str:
        """Generate natural language insight using LLM"""
        
        prompt = f"""You are a business analyst. Explain the analysis results in clear, simple language.

{context}

Provide:
1. A clear answer to the user's question (1-2 sentences)
2. Key findings with specific numbers
3. One actionable recommendation if relevant

Be concise and business-focused."""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a business analyst. Be clear and concise."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=250
        )
        
        return response.choices[0].message.content.strip()
    
    def _calculate_confidence(self, analysis: dict, visualization: dict) -> float:
        """Calculate overall confidence from agent results"""
        confidences = []
        
        if analysis and "confidence" in analysis:
            confidences.append(analysis["confidence"])
        
        if visualization and "confidence" in visualization:
            confidences.append(visualization["confidence"])
        
        return sum(confidences) / len(confidences) if confidences else 0.5
    
    def _list_agents_used(self, analysis: dict, visualization: dict, cleaning: dict) -> list:
        """List which agents contributed"""
        agents = []
        
        if cleaning and not cleaning.get("error"):
            agents.append("cleaning")
        if analysis and not analysis.get("error"):
            agents.append("analysis")
        if visualization and not visualization.get("error"):
            agents.append("visualization")
        
        return agents
