# Add to your FastAPI service
from typing import List, Dict
import json
from fastapi import HTTPException
from sqlalchemy import inspect
from db import configure_db  # Import your existing configure_db function

# This would be added to your main api.py file
# @api.post("/smart-suggestions")
async def get_smart_suggestions(request_data: dict):
    """
    AI-powered query suggestions based on:
    - Database schema analysis
    - User's query history
    - Common business questions
    - Industry best practices
    """
    try:
        db_config = request_data.get('database_config')
        user_history = request_data.get('user_history', [])
        current_context = request_data.get('current_context', '')
        
        # Analyze database schema to understand available data
        schema_analysis = await analyze_database_schema(db_config)
        
        # Generate context-aware suggestions
        suggestions = await generate_smart_suggestions(
            schema_analysis, 
            user_history, 
            current_context
        )
        
        return {
            "suggestions": suggestions,
            "categories": categorize_suggestions(suggestions),
            "trending_queries": get_trending_queries(schema_analysis),
            "business_insights": generate_business_insight_suggestions(schema_analysis)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Smart suggestions failed: {str(e)}")

async def analyze_database_schema(db_config):
    """Analyze database schema to understand data structure"""
    try:
        db, engine = configure_db(
            db_config['dbtype'], db_config['host'], db_config['user'],
            db_config['password'], db_config['dbname']
        )
        
        # Get table information
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        schema_info = {}
        for table in tables:
            columns = inspector.get_columns(table)
            schema_info[table] = {
                'columns': [col['name'] for col in columns],
                'types': {col['name']: str(col['type']) for col in columns},
                'nullable': {col['name']: col['nullable'] for col in columns}
            }
        
        return schema_info
        
    except Exception as e:
        return {}

async def generate_smart_suggestions(schema_analysis, user_history, current_context):
    """Generate intelligent query suggestions"""
    suggestions = []
    
    # Category 1: Schema-based suggestions
    for table, info in schema_analysis.items():
        # Basic exploration queries
        suggestions.append({
            "query": f"Show me an overview of the {table} data",
            "type": "exploration",
            "confidence": 0.9,
            "description": f"Get a sample of data from {table} table"
        })
        
        # Aggregation suggestions for numeric columns
        numeric_cols = [col for col, type_info in info['types'].items() 
                       if 'int' in type_info.lower() or 'float' in type_info.lower() or 'decimal' in type_info.lower()]
        
        for col in numeric_cols:
            suggestions.append({
                "query": f"What is the average {col} in {table}?",
                "type": "aggregation",
                "confidence": 0.8,
                "description": f"Calculate statistics for {col}"
            })
            
        # Time-based suggestions if date columns exist
        date_cols = [col for col, type_info in info['types'].items() 
                    if 'date' in type_info.lower() or 'time' in type_info.lower()]
        
        for date_col in date_cols:
            suggestions.append({
                "query": f"Show me {table} trends over time by {date_col}",
                "type": "temporal",
                "confidence": 0.85,
                "description": f"Analyze trends over {date_col}"
            })
    
    # Category 2: Business intelligence suggestions
    business_suggestions = [
        {
            "query": "What are the top 10 records by value?",
            "type": "business",
            "confidence": 0.7,
            "description": "Find highest performing records"
        },
        {
            "query": "Show me records from the last 30 days",
            "type": "business", 
            "confidence": 0.75,
            "description": "Recent activity analysis"
        },
        {
            "query": "Which categories have the most entries?",
            "type": "business",
            "confidence": 0.8,
            "description": "Distribution analysis"
        }
    ]
    
    suggestions.extend(business_suggestions)
    
    # Category 3: Follow-up suggestions based on context
    if current_context:
        follow_up_suggestions = generate_follow_up_suggestions(current_context)
        suggestions.extend(follow_up_suggestions)
    
    # Sort by confidence and relevance
    suggestions.sort(key=lambda x: x['confidence'], reverse=True)
    
    return suggestions[:15]  # Return top 15 suggestions

def categorize_suggestions(suggestions):
    """Categorize suggestions for better UX"""
    categories = {
        "🔍 Data Exploration": [s for s in suggestions if s['type'] == 'exploration'],
        "📊 Analytics": [s for s in suggestions if s['type'] == 'aggregation'],
        "📈 Trends": [s for s in suggestions if s['type'] == 'temporal'],
        "💼 Business Insights": [s for s in suggestions if s['type'] == 'business']
    }
    
    return {k: v for k, v in categories.items() if v}  # Remove empty categories

def get_trending_queries(schema_analysis):
    """Generate trending/popular query patterns"""
    trending = [
        "Show me the distribution of data across different categories",
        "What patterns can you find in the recent data?",
        "Compare performance metrics across time periods",
        "Identify any unusual or outlier records"
    ]
    
    return trending

def generate_business_insight_suggestions(schema_analysis):
    """Generate business-focused insight suggestions"""
    insights = [
        {
            "title": "Revenue Analysis",
            "description": "Analyze revenue trends and identify growth opportunities",
            "queries": [
                "What is our month-over-month revenue growth?",
                "Which products/services generate the most revenue?",
                "What are our peak sales periods?"
            ]
        },
        {
            "title": "Customer Behavior",
            "description": "Understand customer patterns and preferences", 
            "queries": [
                "Who are our top customers by value?",
                "What is the average customer lifetime value?",
                "Which customer segments are growing fastest?"
            ]
        },
        {
            "title": "Operational Efficiency",
            "description": "Identify operational improvements and bottlenecks",
            "queries": [
                "What are our busiest time periods?",
                "Where are the bottlenecks in our processes?",
                "How can we optimize resource allocation?"
            ]
        }
    ]
    
    return insights

def generate_follow_up_suggestions(context):
    """Generate follow-up questions based on current context"""
    follow_ups = []
    
    context_lower = context.lower()
    
    if 'revenue' in context_lower or 'sales' in context_lower:
        follow_ups.extend([
            {
                "query": "What factors contributed to this revenue?",
                "type": "follow_up",
                "confidence": 0.9,
                "description": "Drill down into revenue drivers"
            },
            {
                "query": "How does this compare to previous periods?",
                "type": "follow_up", 
                "confidence": 0.85,
                "description": "Historical comparison"
            }
        ])
    
    if 'top' in context_lower or 'highest' in context_lower:
        follow_ups.extend([
            {
                "query": "What makes these top performers different?",
                "type": "follow_up",
                "confidence": 0.8,
                "description": "Analyze success factors"
            },
            {
                "query": "Show me the bottom performers for comparison",
                "type": "follow_up",
                "confidence": 0.75,
                "description": "Comparative analysis"
            }
        ])
    
    return follow_ups
