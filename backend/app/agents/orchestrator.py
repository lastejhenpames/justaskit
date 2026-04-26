from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, END
import operator
import pandas as pd
from app.agents.analysis_agent import AnalysisAgent
from app.agents.cleaning_agent import CleaningAgent
from app.agents.visualization_agent import VisualizationAgent
from app.agents.insight_agent import InsightAgent
import logging

logger = logging.getLogger(__name__)

class AgentState(TypedDict):
    query: str
    dataframe: pd.DataFrame
    cleaning: dict
    analysis: dict
    visualization: dict
    insight: dict
    current_agent: str
    agents_executed: Annotated[list, operator.add]
    iteration: int
    max_iterations: int
    error: str | None

class MultiAgentOrchestrator:
    def __init__(self):
        self.cleaning_agent = CleaningAgent()
        self.analysis_agent = AnalysisAgent()
        self.visualization_agent = VisualizationAgent()
        self.insight_agent = InsightAgent()
        self.workflow = self._build_graph()
        self.app = self.workflow.compile()

    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(AgentState)
        workflow.add_node("supervisor", self._supervisor)
        workflow.add_node("cleaning", self._run_cleaning)
        workflow.add_node("analysis", self._run_analysis)
        workflow.add_node("visualization", self._run_visualization)
        workflow.add_node("insight", self._run_insight)
        workflow.set_entry_point("supervisor")
        workflow.add_conditional_edges(
            "supervisor",
            self._route_from_supervisor,
            {
                "cleaning": "cleaning",
                "analysis": "analysis",
                "visualization": "visualization",
                "insight": "insight",
                "end": END
            }
        )
        for agent in ["cleaning", "analysis", "visualization"]:
            workflow.add_conditional_edges(
                agent,
                self._should_retry,
                {
                    "retry": "supervisor",
                    "continue": "supervisor"
                }
            )
        workflow.add_edge("insight", END)
        return workflow

    def _supervisor(self, state: AgentState) -> AgentState:
        query_lower = state["query"].lower()
        agents_done = set(state.get("agents_executed", []))
        
        # Step 1: Cleaning (if needed)
        if "cleaning" not in agents_done:
            if any(word in query_lower for word in ["clean", "missing", "null", "invalid"]):
                return {"current_agent": "cleaning"}
        
        # Step 2: Analysis (always needed)
        if "analysis" not in agents_done:
            return {"current_agent": "analysis"}
        
        # Step 3: Visualization (only if explicitly requested or query suggests comparison/ranking)
        if "visualization" not in agents_done:
            # Check if visualization is explicitly requested
            viz_keywords = ["show", "chart", "graph", "plot", "visualize", "display"]
            # Check if query suggests comparison or ranking (which benefits from viz)
            comparison_keywords = ["top", "compare", "by", "versus", "vs", "highest", "lowest", "best", "worst"]
            
            has_viz_keyword = any(word in query_lower for word in viz_keywords)
            has_comparison = any(word in query_lower for word in comparison_keywords)
            
            # Also check if analysis returned multiple data points (good for visualization)
            analysis_result = state.get("analysis", {}).get("result")
            has_multiple_results = False
            if isinstance(analysis_result, (list, dict)):
                if isinstance(analysis_result, list) and len(analysis_result) > 1:
                    has_multiple_results = True
                elif isinstance(analysis_result, dict) and len(analysis_result) > 1:
                    has_multiple_results = True
            
            # Run visualization if explicitly requested OR if it's a comparison with multiple results
            if has_viz_keyword or (has_comparison and has_multiple_results):
                logger.info(f"Visualization triggered: viz_keyword={has_viz_keyword}, comparison={has_comparison}, multiple_results={has_multiple_results}")
                return {"current_agent": "visualization"}
            else:
                logger.info(f"Skipping visualization: query doesn't require visual representation")
        
        # Step 4: Insight (always final step)
        return {"current_agent": "insight"}
    
    def _route_from_supervisor(self, state: AgentState) -> str:
        current = state.get("current_agent", "analysis")
        if state.get("iteration", 0) >= state.get("max_iterations", 3):
            logger.warning(f"Max iterations reached, moving to insight")
            return "insight"
        return current

    def _run_cleaning(self, state: AgentState) -> AgentState:
        logger.info("Running cleaning agent")
        try:
            result = self.cleaning_agent.clean(state["dataframe"])
            return {
                "cleaning": result,
                "agents_executed": ["cleaning"],
                "dataframe": result.get("cleaned_df", state["dataframe"])
            }
        except Exception as e:
            logger.error(f"Cleaning agent error: {str(e)}")
            return {
                "cleaning": {"error": str(e)},
                "agents_executed": ["cleaning"]
            }
    
    def _run_analysis(self, state: AgentState) -> AgentState:
        logger.info("Running analysis agent")
        try:
            result = self.analysis_agent.analyze(state["dataframe"], state["query"])
            return {
                "analysis": result,
                "agents_executed": ["analysis"],
                "iteration": state.get("iteration", 0) + 1
            }
        except Exception as e:
            logger.error(f"Analysis agent error: {str(e)}")
            return {
                "analysis": {"error": str(e)},
                "agents_executed": ["analysis"],
                "iteration": state.get("iteration", 0) + 1
            }

    def _run_visualization(self, state: AgentState) -> AgentState:
        logger.info("Running visualization agent")
        try:
            result = self.visualization_agent.create_chart(
                state["dataframe"],
                state["query"],
                state.get("analysis", {})
            )
            return {
                "visualization": result,
                "agents_executed": ["visualization"]
            }
        except Exception as e:
            logger.error(f"Visualization agent error: {str(e)}")
            return {
                "visualization": {"error": str(e)},
                "agents_executed": ["visualization"]
            }
    
    def _run_insight(self, state: AgentState) -> AgentState:
        logger.info("Running insight agent")
        try:
            result = self.insight_agent.generate_insight(
                query=state["query"],
                analysis=state.get("analysis", {}),
                visualization=state.get("visualization", {}),
                cleaning=state.get("cleaning", {})
            )
            return {
                "insight": result,
                "agents_executed": ["insight"]
            }
        except Exception as e:
            logger.error(f"Insight agent error: {str(e)}")
            return {
                "insight": {"error": str(e)},
                "agents_executed": ["insight"],
                "error": str(e)
            }

    def _should_retry(self, state: AgentState) -> Literal["retry", "continue"]:
        # Removed retry logic - just continue
        return "continue"
        if confidence < 0.7 and iteration < max_iterations:
            logger.info(f"{current_agent} confidence {confidence:.2f} is low, retrying")
            return "retry"
        return "continue"
    
    def execute(self, df: pd.DataFrame, query: str) -> dict:
        initial_state = {
            "query": query,
            "dataframe": df,
            "cleaning": {},
            "analysis": {},
            "visualization": {},
            "insight": {},
            "current_agent": "",
            "agents_executed": [],
            "iteration": 0,
            "max_iterations": 3,
            "final_confidence": 0.0,
            "error": None
        }
        try:
            final_state = self.app.invoke(initial_state)
            return {
                "type": "multi_agent",
                "query": query,
                "agents_executed": final_state.get("agents_executed", []),
                "analysis": final_state.get("analysis", {}),
                "visualization": final_state.get("visualization", {}),
                "insight": final_state.get("insight", {}),
                "confidence": final_state.get("final_confidence", 0.0),
                "iterations": final_state.get("iteration", 0),
                "error": final_state.get("error")
            }
        except Exception as e:
            logger.error(f"Orchestrator execution error: {str(e)}")
            return {
                "type": "error",
                "query": query,
                "error": str(e),
                "confidence": 0.0
            }
