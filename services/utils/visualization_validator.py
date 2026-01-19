"""
Visualization Validator using Google Gemini
This module uses Google Gemini to intelligently determine:
1. Whether a query result should be visualized
2. Which chart types are appropriate for the data
"""

import os
import json
from typing import List, Dict, Optional, Any
from dotenv import load_dotenv
import logging
import google.generativeai as genai

load_dotenv()

class VisualizationValidator:
    def __init__(self):
        """Initialize Google Gemini client for visualization validation"""
        self.logger = logging.getLogger(__name__)
        
        # Google Gemini credentials
        self.api_key = os.getenv("GEMINI_API_KEY")
        
        if not self.api_key:
            self.logger.warning("⚠️ Google Gemini API key not configured. Visualization validation will use fallback logic.")
            self.model = None
        else:
            try:
                genai.configure(api_key=self.api_key)
                # Use Gemini 2.5 Flash
                self.model = genai.GenerativeModel('gemini-2.5-flash')
                self.logger.info("✅ Google Gemini client initialized for visualization validation (gemini-2.5-flash)")
            except Exception as e:
                self.logger.error(f"❌ Failed to initialize Google Gemini: {e}")
                self.model = None
    
    def should_visualize(
        self, 
        user_query: str, 
        sql_query: str, 
        result_data: List[Dict[str, Any]],
        result_count: int
    ) -> Dict[str, Any]:
        """
        Determine if query results should be visualized and which charts to use.
        
        Args:
            user_query: Original natural language query
            sql_query: Generated SQL/Cypher query
            result_data: Query result data (sample)
            result_count: Total number of rows returned
            
        Returns:
            {
                "should_visualize": bool,
                "reason": str,
                "recommended_charts": List[str],
                "confidence": float
            }
        """
        
        # Quick validation checks
        if not result_data or result_count == 0:
            return {
                "should_visualize": False,
                "reason": "No data returned from query",
                "recommended_charts": [],
                "confidence": 1.0,
                "validator": "rule_based"
            }
        
        if not self.model:
            # Fallback to rule-based logic if Gemini not available
            return self._fallback_validation(user_query, sql_query, result_data, result_count)
        
        try:
            # Prepare data summary for Gemini
            data_summary = self._prepare_data_summary(result_data, result_count)
            
            # Create prompt for Gemini
            prompt = self._create_validation_prompt(user_query, sql_query, data_summary)
            
            # Call Google Gemini
            response = self.model.generate_content(prompt)
            
            # Parse response
            content = response.text
            
            # Extract JSON from response (Gemini might wrap it in markdown)
            content = content.strip()
            if content.startswith('```json'):
                content = content[7:]
            if content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            
            result = json.loads(content)
            
            # Validate and clean response
            result = self._validate_response(result)
            # mark source
            result["validator"] = "gemini"
            
            self.logger.info(f"✅ Gemini validation: {result['should_visualize']} - {result['reason']}")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Gemini validation failed: {e}")
            # Fallback to rule-based logic
            fallback = self._fallback_validation(user_query, sql_query, result_data, result_count)
            # ensure validator field
            fallback.setdefault("validator", "rule_based")
            return fallback
    
    def _prepare_data_summary(self, result_data: List[Dict], result_count: int) -> Dict:
        """Prepare a summary of the data for Gemini analysis"""
        if not result_data:
            return {
                "row_count": 0,
                "columns": [],
                "sample_row": {}
            }
        
        sample = result_data[0] if result_data else {}
        
        # Analyze column types
        column_info = []
        for key, value in sample.items():
            col_type = "unknown"
            if isinstance(value, (int, float)):
                col_type = "numeric"
            elif isinstance(value, str):
                # Check if it's a date-like string
                if any(keyword in key.lower() for keyword in ['date', 'time', 'year', 'month', 'day']):
                    col_type = "temporal"
                elif value.replace('.', '').replace('-', '').isdigit():
                    col_type = "numeric_string"
                else:
                    col_type = "categorical"
            elif isinstance(value, bool):
                col_type = "boolean"
            
            column_info.append({
                "name": key,
                "type": col_type,
                "sample_value": str(value)[:50]  # Limit length
            })
        
        return {
            "row_count": result_count,
            "column_count": len(column_info),
            "columns": column_info,
            "sample_rows": result_data[:3]  # First 3 rows
        }
    
    def _create_validation_prompt(
        self, 
        user_query: str, 
        sql_query: str, 
        data_summary: Dict
    ) -> str:
        """Create the prompt for Gemini"""
        return f"""Analyze this database query and determine if visualization is appropriate. BE CONSERVATIVE - only visualize when charts add clear value.

USER QUERY: "{user_query}"

SQL QUERY: {sql_query}

RESULT DATA SUMMARY:
- Total rows: {data_summary['row_count']}
- Columns: {data_summary['column_count']}
- Column details: {json.dumps(data_summary['columns'], indent=2)}
- Sample data: {json.dumps(data_summary['sample_rows'], indent=2)}

Should this data be visualized? If yes, which chart types are most appropriate?

STRICT RULES (err on the side of NO visualization):
- Simple lookups (e.g., "who is X", "what is Y", "find employee") → NO visualization
- Simple lists WITHOUT aggregation (e.g., "list all X", "show all Y names", "get all Z") → NO visualization
- Lists with just names/IDs and descriptive fields (name + qualification, name + department) → NO visualization
- Only 1-2 columns without numeric metrics → NO visualization
- Lists asking for "all", "names", "details", "information" → NO visualization

VISUALIZE ONLY WHEN:
- Aggregations/metrics present (COUNT, SUM, AVG, MAX, MIN)
- Explicit comparison requested ("compare X vs Y")
- Trends over time ("sales by month", "growth over years")
- Distributions ("top 10", "breakdown by category")
- Correlations between numeric values

Respond ONLY with valid JSON in this exact format:
{{
    "should_visualize": true/false,
    "reason": "brief explanation why visualization is/isn't appropriate",
    "recommended_charts": ["chart1", "chart2", "chart3"],
    "confidence": 0.0-1.0
}}

Available chart types: bar, line, pie, area, scatter, heatmap
Recommend max 3 chart types, ordered by appropriateness."""
    
    def _validate_response(self, result: Dict) -> Dict:
        """Validate and clean Gemini response"""
        # Ensure required fields
        if "should_visualize" not in result:
            result["should_visualize"] = False
        
        if "reason" not in result:
            result["reason"] = "Unable to determine visualization appropriateness"
        
        if "recommended_charts" not in result:
            result["recommended_charts"] = []
        
        if "confidence" not in result:
            result["confidence"] = 0.5
        
        # Validate chart types
        valid_charts = ["bar", "line", "pie", "area", "scatter", "heatmap"]
        result["recommended_charts"] = [
            chart.lower() for chart in result["recommended_charts"] 
            if chart.lower() in valid_charts
        ][:3]  # Max 3 charts
        
        # If should_visualize is True but no charts recommended, add defaults
        if result["should_visualize"] and not result["recommended_charts"]:
            result["recommended_charts"] = ["bar", "pie"]
        
        # If should_visualize is False, clear chart recommendations
        if not result["should_visualize"]:
            result["recommended_charts"] = []
        
        return result
    
    def _fallback_validation(
        self, 
        user_query: str, 
        sql_query: str, 
        result_data: List[Dict], 
        result_count: int
    ) -> Dict:
        """Fallback rule-based validation when Gemini is unavailable"""
        
        user_query_lower = user_query.lower()
        sql_query_lower = sql_query.lower()
        
        # Keywords that indicate NO visualization needed
        no_viz_keywords = [
            "who is", "who's", "what is", "what's", "which is",
            "find the manager", "get the email", "show me the name",
            "return the", "get the password", "find the address",
            "list all", "show all", "get all", "display all",
            "list the", "show the", "get the", "display the",
            "names of", "details of", "information about"
        ]
        
        # Check for simple lookup/list queries
        for keyword in no_viz_keywords:
            if keyword in user_query_lower:
                return {
                    "should_visualize": False,
                    "reason": "Simple lookup/list query - visualization not meaningful",
                    "recommended_charts": [],
                    "confidence": 0.9
                }
        
        # Check for single row results
        if result_count == 1 and len(result_data[0]) <= 3:
            return {
                "should_visualize": False,
                "reason": "Single result with few fields - better shown as text",
                "recommended_charts": [],
                "confidence": 0.85
            }
        
        # Check if result is just a list without metrics (2 or fewer columns, no aggregation)
        if result_data and len(result_data[0]) <= 2:
            cols = list(result_data[0].keys())
            # Check if columns are just descriptive (names, IDs, titles, etc.)
            descriptive_keywords = ['name', 'id', 'email', 'title', 'description', 'address', 'phone', 'qualification', 'department', 'city', 'state']
            all_descriptive = all(
                any(keyword in col.lower() for keyword in descriptive_keywords)
                for col in cols
            )
            
            if all_descriptive:
                return {
                    "should_visualize": False,
                    "reason": "Simple list without metrics - visualization not informative",
                    "recommended_charts": [],
                    "confidence": 0.85
                }
        
        # Keywords that indicate YES visualization needed
        viz_keywords = [
            "compare", "comparison", "trend", "over time", "distribution",
            "count", "total", "average", "sum", "top", "bottom",
            "most", "least", "highest", "lowest", "growth", "each"
        ]
        
        has_viz_keyword = any(keyword in user_query_lower for keyword in viz_keywords)
        has_aggregation = any(keyword in sql_query_lower for keyword in ['count', 'sum', 'avg', 'max', 'min', 'group by'])
        
        if has_viz_keyword or has_aggregation:
            # Determine chart types based on query
            charts = []
            
            if "over time" in user_query_lower or "trend" in user_query_lower:
                charts = ["line", "area", "bar"]
            elif result_count <= 10 and has_aggregation:
                charts = ["pie", "bar", "line"]
            elif "compare" in user_query_lower or "comparison" in user_query_lower:
                charts = ["bar", "line", "scatter"]
            else:
                charts = ["bar", "pie", "line"]
            
            return {
                "should_visualize": True,
                "reason": "Query involves aggregation/comparison - suitable for visualization",
                "recommended_charts": charts,
                "confidence": 0.75
            }
        
        # Default to no visualization unless clear benefit
        return {
            "should_visualize": False,
            "reason": "No clear visualization indicators - better shown as table",
            "recommended_charts": [],
            "confidence": 0.7
        }


# Singleton instance
_validator_instance = None

def get_visualization_validator() -> VisualizationValidator:
    """Get or create the singleton VisualizationValidator instance"""
    global _validator_instance
    if _validator_instance is None:
        _validator_instance = VisualizationValidator()
    return _validator_instance
