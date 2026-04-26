from openai import OpenAI
from app.core.config import settings
import pandas as pd
import json
import logging
import ast

logger = logging.getLogger(__name__)

class QueryAgent:
    """Agent that converts natural language to pandas operations"""
    
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL
        )
        self.model = settings.OPENAI_MODEL
    
    def analyze(self, df: pd.DataFrame, query: str) -> dict:
        """
        Convert natural language query to pandas operation and execute
        
        Args:
            df: DataFrame to analyze
            query: Natural language query
        
        Returns:
            dict with analysis results
        """
        try:
            # Get schema info
            schema_info = self._get_schema_info(df)
            
            # Generate pandas code using LLM
            pandas_code = self._generate_pandas_code(query, schema_info)
            
            # Execute the code safely
            result = self._execute_code(df, pandas_code)
            
            # Generate insight
            insight = self._generate_insight(query, result, df)
            
            return {
                "type": "llm_analysis",
                "query": query,
                "pandas_code": pandas_code,
                "result": result,
                "insight": insight["text"]
            }
            
        except Exception as e:
            logger.error(f"Query agent error: {str(e)}")
            return {
                "type": "error",
                "query": query,
                "insight": f"Could not process query: {str(e)}"
            }
    
    def _get_schema_info(self, df: pd.DataFrame) -> str:
        """Get DataFrame schema information"""
        info = {
            "columns": list(df.columns),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "shape": df.shape,
            "sample": df.head(3).to_dict(orient='records')
        }
        return json.dumps(info, indent=2)
    
    def _generate_pandas_code(self, query: str, schema_info: str) -> str:
        """Generate pandas code from natural language query"""
        
        prompt = f"""You are a data analysis expert. Convert the user's question into pandas code.

Dataset Schema:
{schema_info}

User Question: {query}

Generate ONLY the pandas code needed to answer this question. Return a single expression that can be evaluated.
Use 'df' as the DataFrame variable name.

Examples:
- "total revenue" -> df['revenue'].sum()
- "average price" -> df['price'].mean()
- "top 5 products by sales" -> df.nlargest(5, 'sales')[['product', 'sales']].to_dict('records')
- "revenue by category" -> df.groupby('category')['revenue'].sum().to_dict()

Return ONLY the pandas code, no explanations or markdown."""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a pandas expert. Return only executable pandas code."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=200
        )
        
        code = response.choices[0].message.content.strip()
        # Clean up markdown code blocks if present
        code = code.replace("```python", "").replace("```", "").strip()
        
        logger.info(f"Generated pandas code: {code}")
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
                
                # Block attribute access to dunder methods
                if isinstance(node, ast.Attribute):
                    if node.attr.startswith('__') and node.attr.endswith('__'):
                        logger.warning(f"Blocked dunder attribute access: {node.attr}")
                        return False
                
                # Block dangerous functions
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
        try:
            # Validate code safety first
            if not self._validate_code_safety(code):
                raise ValueError("Generated code contains unsafe operations")
            
            # Create safe execution environment
            safe_globals = {
                "df": df,
                "pd": pd,
                "__builtins__": {}  # Restrict built-in functions for safety
            }
            
            result = eval(code, safe_globals)
            
            # Convert result to JSON-serializable format
            if isinstance(result, pd.Series):
                result = result.to_dict()
            elif isinstance(result, pd.DataFrame):
                result = result.to_dict(orient='records')
            elif isinstance(result, (pd.Timestamp, pd.Timedelta)):
                result = str(result)
            elif hasattr(result, 'item'):  # numpy types
                result = result.item()
            
            return result
            
        except Exception as e:
            logger.error(f"Code execution error: {str(e)}")
            raise Exception(f"Failed to execute analysis: {str(e)}")
    
    def _generate_insight(self, query: str, result: any, df: pd.DataFrame) -> dict:
        """Generate natural language insight from results"""
        
        prompt = f"""You are a business analyst. Explain the analysis result in simple terms.

User Question: {query}
Analysis Result: {json.dumps(result, default=str)}
Dataset has {len(df)} rows.

Provide a clear, concise explanation (1-2 sentences).

Return JSON format:
{{"text": "explanation here"}}"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a business analyst. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=150
        )
        
        try:
            insight = json.loads(response.choices[0].message.content.strip())
            return insight
        except:
            # Fallback if JSON parsing fails
            return {
                "text": response.choices[0].message.content.strip()
            }
