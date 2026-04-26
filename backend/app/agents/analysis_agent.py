from openai import OpenAI
from app.core.config import settings
import pandas as pd
import json
import logging
import ast

logger = logging.getLogger(__name__)

class AnalysisAgent:
    """
    Specialist agent for data analysis
    Generates and executes pandas code based on queries
    """
    
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL
        )
        self.model = settings.OPENAI_MODEL
    
    def analyze(self, df: pd.DataFrame, query: str) -> dict:
        """
        Analyze data based on query
        
        Returns:
            dict with analysis results and confidence score
        """
        try:
            # Get schema
            schema = self._get_schema(df)
            
            # Generate pandas code
            code = self._generate_code(query, schema)
            
            # Execute code
            result = self._execute_code(df, code)
            
            # Calculate confidence
            confidence = self._calculate_confidence(df, result)
            
            return {
                "pandas_code": code,
                "result": result,
                "confidence": confidence,
                "row_count": len(df),
                "columns_used": self._extract_columns_from_code(code)
            }
            
        except Exception as e:
            logger.error(f"Analysis error: {str(e)}")
            return {
                "error": str(e),
                "confidence": 0.0
            }
    
    def _get_schema(self, df: pd.DataFrame) -> str:
        """Get DataFrame schema info"""
        info = {
            "columns": list(df.columns),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "shape": df.shape,
            "sample": df.head(2).to_dict(orient='records')
        }
        return json.dumps(info, indent=2)
    
    def _generate_code(self, query: str, schema: str) -> str:
        """Generate pandas code using LLM"""
        
        prompt = f"""Generate pandas code to answer this query.

Dataset Schema:
{schema}

Query: {query}

IMPORTANT RULES:
- Return ONLY executable pandas code
- Use 'df' as the DataFrame variable
- DO NOT use matplotlib, plotly, or any plotting libraries
- DO NOT use plt, sns, or any visualization code
- Return data analysis code only
- Code must be a single expression that returns a value

Examples:
- "total revenue" -> df['revenue'].sum()
- "top 3 by revenue" -> df.nlargest(3, 'revenue')[['product', 'revenue']].to_dict('records')
- "average by category" -> df.groupby('category')['revenue'].mean().to_dict()

Return only the code, nothing else:"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a pandas expert. Return only data analysis code, no plotting."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=200
        )
        
        code = response.choices[0].message.content.strip()
        
        # Clean up the code - remove markdown, comments, extra text
        code = code.replace("```python", "").replace("```", "").strip()
        
        # Remove any lines that are comments or explanations
        lines = code.split('\n')
        code_lines = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('//'):
                # Skip lines with plotting code
                if not any(plot_lib in line.lower() for plot_lib in ['plt.', 'sns.', 'plotly', 'matplotlib', 'seaborn']):
                    code_lines.append(line)
        
        code = '\n'.join(code_lines) if code_lines else code
        
        # If multiple lines, take the last one (usually the actual code)
        if '\n' in code:
            code = code.split('\n')[-1].strip()
        
        logger.info(f"Generated code: {code}")
        
        return code
    
    def _validate_code_safety(self, code: str) -> bool:
        """
        Validate that code only uses safe operations
        Prevents code injection attacks
        """
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                # Block imports
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    logger.warning(f"Blocked import statement in code: {code}")
                    return False
                
                # Block attribute access to dunder methods (e.g., __class__, __bases__)
                if isinstance(node, ast.Attribute):
                    if node.attr.startswith('__') and node.attr.endswith('__'):
                        logger.warning(f"Blocked dunder attribute access: {node.attr}")
                        return False
                
                # Block exec, eval, compile
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in ['exec', 'eval', 'compile', '__import__']:
                            logger.warning(f"Blocked dangerous function: {node.func.id}")
                            return False
            
            return True
        except SyntaxError as e:
            logger.error(f"Syntax error in generated code: {e}")
            return False
    
    def _execute_code(self, df: pd.DataFrame, code: str) -> any:
        """Safely execute pandas code with AST validation"""
        import numpy as np
        
        # Validate code safety first
        if not self._validate_code_safety(code):
            raise ValueError("Generated code contains unsafe operations")
        
        safe_globals = {
            "df": df,
            "pd": pd,
            "np": np,
            "__builtins__": {
                "len": len,
                "sum": sum,
                "min": min,
                "max": max,
                "abs": abs,
                "round": round,
                "int": int,
                "float": float,
                "str": str,
                "list": list,
                "dict": dict,
                "range": range,
            }
        }
        
        result = eval(code, safe_globals)
        
        # Convert to JSON-serializable
        if isinstance(result, pd.Series):
            result = result.to_dict()
        elif isinstance(result, pd.DataFrame):
            result = result.to_dict(orient='records')
        elif hasattr(result, 'item'):
            result = result.item()
        
        return result
    
    def _calculate_confidence(self, df: pd.DataFrame, result: any) -> float:
        """
        Calculate confidence score based on:
        - Data quality (missing values, size)
        - Result validity
        """
        confidence = 0.8  # Base confidence
        
        # Penalize for small datasets
        if len(df) < 10:
            confidence -= 0.2
        
        # Penalize for missing values
        missing_pct = df.isnull().sum().sum() / (len(df) * len(df.columns))
        confidence -= missing_pct * 0.3
        
        # Boost for valid numeric results
        if isinstance(result, (int, float)) and result > 0:
            confidence += 0.1
        
        return max(0.0, min(1.0, confidence))
    
    def _extract_columns_from_code(self, code: str) -> list:
        """Extract column names referenced in code"""
        columns = []
        for part in code.split("'"):
            if part and not part.startswith("df"):
                columns.append(part)
        return list(set(columns))[:5]  # Limit to 5
