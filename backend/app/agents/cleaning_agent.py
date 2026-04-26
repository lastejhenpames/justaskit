import pandas as pd
import logging

logger = logging.getLogger(__name__)

class CleaningAgent:
    """
    Specialist agent for data cleaning
    Handles missing values, type conversions, outliers
    """
    
    def clean(self, df: pd.DataFrame) -> dict:
        """
        Clean the DataFrame
        
        Returns:
            dict with cleaned DataFrame and cleaning report
        """
        try:
            cleaned_df = df.copy()
            report = {
                "actions": [],
                "before": {
                    "rows": len(df),
                    "missing_values": int(df.isnull().sum().sum())
                }
            }
            
            # Handle missing values
            for col in cleaned_df.columns:
                missing_count = cleaned_df[col].isnull().sum()
                if missing_count > 0:
                    if cleaned_df[col].dtype in ['int64', 'float64']:
                        # Fill numeric with median
                        cleaned_df[col].fillna(cleaned_df[col].median(), inplace=True)
                        report["actions"].append(f"Filled {missing_count} missing values in '{col}' with median")
                    else:
                        # Fill categorical with mode
                        mode_val = cleaned_df[col].mode()[0] if not cleaned_df[col].mode().empty else "Unknown"
                        cleaned_df[col].fillna(mode_val, inplace=True)
                        report["actions"].append(f"Filled {missing_count} missing values in '{col}' with mode")
            
            # Remove duplicates
            dup_count = cleaned_df.duplicated().sum()
            if dup_count > 0:
                cleaned_df.drop_duplicates(inplace=True)
                report["actions"].append(f"Removed {dup_count} duplicate rows")
            
            report["after"] = {
                "rows": len(cleaned_df),
                "missing_values": int(cleaned_df.isnull().sum().sum())
            }
            
            # Calculate confidence
            confidence = self._calculate_confidence(df, cleaned_df, report)
            
            return {
                "cleaned_df": cleaned_df,
                "report": report,
                "confidence": confidence
            }
            
        except Exception as e:
            logger.error(f"Cleaning error: {str(e)}")
            return {
                "cleaned_df": df,
                "error": str(e),
                "confidence": 0.0
            }
    
    def _calculate_confidence(self, original_df: pd.DataFrame, cleaned_df: pd.DataFrame, report: dict) -> float:
        """Calculate cleaning confidence"""
        confidence = 0.9  # Base confidence
        
        # Penalize if we lost too many rows
        rows_lost = len(original_df) - len(cleaned_df)
        if rows_lost > len(original_df) * 0.1:  # Lost >10% of data
            confidence -= 0.2
        
        # Boost if we fixed missing values
        if report["before"]["missing_values"] > 0 and report["after"]["missing_values"] == 0:
            confidence += 0.1
        
        return max(0.0, min(1.0, confidence))
