import pandas as pd
import json
import logging

logger = logging.getLogger(__name__)

class VisualizationAgent:
    """
    Specialist agent for creating visualizations
    Generates visx-compatible chart data based on analysis results
    """
    
    def create_chart(self, df: pd.DataFrame, query: str, analysis: dict) -> dict:
        """
        Create visualization based on query and analysis
        
        Returns:
            dict with visx-compatible chart data and metadata
        """
        try:
            # Determine chart type from query
            chart_type = self._determine_chart_type(query, analysis)
            logger.info(f"Creating {chart_type} chart for query: {query[:50]}...")
            
            # Generate visx-compatible chart data
            chart_data = self._generate_chart_data(df, chart_type, analysis)
            
            if chart_data is None:
                logger.warning("Chart generation returned None")
                return {
                    "chart_type": chart_type,
                    "chart_json": None,
                    "error": "Could not generate chart from data"
                }
            
            logger.info(f"Chart data generated successfully: {chart_type}")
            
            return {
                "chart_type": chart_type,
                "chart_json": {"data": chart_data}  # Wrap in data key for frontend
            }
            
        except Exception as e:
            logger.error(f"Visualization error: {str(e)}", exc_info=True)
            return {
                "chart_type": "unknown",
                "chart_json": None,
                "error": str(e),
                "confidence": 0.0
            }
    
    def _determine_chart_type(self, query: str, analysis: dict) -> str:
        """Determine appropriate chart type"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["trend", "over time", "timeline"]):
            return "line"
        elif any(word in query_lower for word in ["compare", "by", "category"]):
            return "bar"
        elif any(word in query_lower for word in ["distribution", "histogram"]):
            return "histogram"
        elif any(word in query_lower for word in ["correlation", "relationship"]):
            return "scatter"
        else:
            # Default based on result type
            result = analysis.get("result", {})
            if isinstance(result, dict) and len(result) > 1:
                return "bar"
            return "bar"
    
    def _generate_chart_data(self, df: pd.DataFrame, chart_type: str, analysis: dict) -> list:
        """
        Generate visx-compatible chart data
        Returns list of traces with format: [{ x: [...], y: [...], type: 'bar'|'line', name: '...', marker: {...} }]
        """
        
        result = analysis.get("result", {})
        
        if chart_type == "bar":
            if isinstance(result, dict) and len(result) > 0:
                # Simple bar chart from dict
                return [{
                    "x": [str(k) for k in result.keys()],
                    "y": list(result.values()),
                    "type": "bar",
                    "name": "Value",
                    "marker": {"color": "#a855f7"}  # Purple
                }]
            elif isinstance(result, list) and len(result) > 0:
                # Bar chart from list of dicts
                result_df = pd.DataFrame(result)
                keys = list(result_df.columns)
                if len(keys) >= 2:
                    # Use first key as x, second as y
                    return [{
                        "x": [str(x) for x in result_df[keys[0]].tolist()],
                        "y": result_df[keys[1]].tolist(),
                        "type": "bar",
                        "name": keys[1].title(),
                        "marker": {"color": "#a855f7"}
                    }]
                else:
                    return None
            else:
                # Fallback: use first numeric column
                numeric_cols = df.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 0:
                    top_10 = df.head(10)
                    return [{
                        "x": [str(i) for i in range(len(top_10))],
                        "y": top_10[numeric_cols[0]].tolist(),
                        "type": "bar",
                        "name": numeric_cols[0],
                        "marker": {"color": "#a855f7"}
                    }]
                else:
                    return None
        
        elif chart_type == "line":
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                return [{
                    "x": [str(i) for i in range(len(df))],
                    "y": df[numeric_cols[0]].tolist(),
                    "type": "line",
                    "name": numeric_cols[0],
                    "marker": {"color": "#38bdf8"}  # Cyan
                }]
            else:
                return None
        
        else:
            # Default bar chart
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                top_10 = df.head(10)
                return [{
                    "x": [str(i) for i in range(len(top_10))],
                    "y": top_10[numeric_cols[0]].tolist(),
                    "type": "bar",
                    "name": numeric_cols[0],
                    "marker": {"color": "#a855f7"}
                }]
            else:
                return None
