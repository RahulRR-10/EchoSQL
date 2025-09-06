"""
RAG (Retrieval-Augmented Generation) Service for Query History
This module provides intelligent context retrieval from MongoDB query history
to enhance LLM responses with relevant past queries and patterns.
"""

import os
import json
from typing import List, Dict, Optional, Any
from pymongo import MongoClient
from dotenv import load_dotenv
import logging
from datetime import datetime, timedelta
import re
from difflib import SequenceMatcher

load_dotenv()

class RAGService:
    def __init__(self):
        """Initialize RAG service with MongoDB connection"""
        # Setup logging first
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        self.mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        self.db_name = os.getenv("MONGODB_DB_NAME", "aura")
        self.client = None
        self.db = None
        self.query_collection = None
        self._initialize_connection()
        
        # Configuration
        self.similarity_threshold = 0.3  # Minimum similarity score for relevance
        self.max_context_queries = 5    # Maximum number of past queries to include
        self.recent_days = 30           # Only consider queries from last N days
    
    def _initialize_connection(self):
        """Initialize MongoDB connection"""
        try:
            self.client = MongoClient(self.mongo_uri)
            self.db = self.client[self.db_name]
            self.query_collection = self.db["querymessages"]
            
            # Test connection
            self.client.admin.command('ping')
            self.logger.info("✅ MongoDB connection established for RAG service")
            
        except Exception as e:
            self.logger.warning(f"⚠️ MongoDB connection failed: {e}. RAG will operate in fallback mode.")
            self.client = None
            self.db = None
            self.query_collection = None
    
    def _calculate_similarity(self, query1: str, query2: str) -> float:
        """Calculate semantic similarity between two queries"""
        if not query1 or not query2:
            return 0.0
        
        # Normalize queries for comparison
        q1_norm = self._normalize_query(query1)
        q2_norm = self._normalize_query(query2)
        
        # Use SequenceMatcher for basic similarity
        similarity = SequenceMatcher(None, q1_norm, q2_norm).ratio()
        
        # Boost similarity for common database terms
        common_terms = self._extract_common_terms(q1_norm, q2_norm)
        if common_terms:
            similarity += len(common_terms) * 0.1
        
        return min(similarity, 1.0)
    
    def _normalize_query(self, query: str) -> str:
        """Normalize query for better comparison"""
        # Convert to lowercase and remove extra whitespace
        normalized = re.sub(r'\s+', ' ', query.lower().strip())
        
        # Remove common words that don't add semantic value
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        words = [word for word in normalized.split() if word not in stop_words]
        
        return ' '.join(words)
    
    def _extract_common_terms(self, query1: str, query2: str) -> List[str]:
        """Extract common database-related terms between queries"""
        # Database keywords that indicate similar intent
        db_keywords = {
            'select', 'count', 'sum', 'avg', 'max', 'min', 'group', 'order', 'where',
            'join', 'inner', 'left', 'right', 'having', 'distinct', 'limit',
            'user', 'users', 'customer', 'customers', 'order', 'orders', 'product', 'products',
            'total', 'revenue', 'sales', 'profit', 'top', 'bottom', 'highest', 'lowest',
            'show', 'find', 'get', 'list', 'display', 'analyze', 'report'
        }
        
        words1 = set(query1.split())
        words2 = set(query2.split())
        
        # Find common words that are database-related
        common = words1.intersection(words2).intersection(db_keywords)
        return list(common)
    
    def _extract_query_intent(self, query: str) -> Dict[str, Any]:
        """Extract semantic intent from query for better matching"""
        intent = {
            'action': None,
            'entities': [],
            'aggregation': None,
            'keywords': []
        }
        
        query_lower = query.lower()
        
        # Extract action intent
        if any(word in query_lower for word in ['count', 'how many', 'number of']):
            intent['action'] = 'count'
        elif any(word in query_lower for word in ['sum', 'total', 'aggregate']):
            intent['action'] = 'sum'
        elif any(word in query_lower for word in ['avg', 'average', 'mean']):
            intent['action'] = 'average'
        elif any(word in query_lower for word in ['max', 'maximum', 'highest', 'top']):
            intent['action'] = 'max'
        elif any(word in query_lower for word in ['min', 'minimum', 'lowest', 'bottom']):
            intent['action'] = 'min'
        elif any(word in query_lower for word in ['show', 'list', 'display', 'get', 'find']):
            intent['action'] = 'select'
        
        # Extract entities (table/domain concepts)
        entities = ['user', 'customer', 'order', 'product', 'sale', 'revenue', 'profit', 'item']
        for entity in entities:
            if entity in query_lower:
                intent['entities'].append(entity)
        
        # Extract keywords
        intent['keywords'] = self._normalize_query(query).split()
        
        return intent
    
    def retrieve_relevant_context(self, current_query: str, database_config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Retrieve relevant context from query history for the current query
        
        Args:
            current_query: The user's current query
            database_config: Database configuration to match similar contexts
            
        Returns:
            Dictionary containing relevant context or None if no relevant context found
        """
        if self.query_collection is None:
            self.logger.warning("❌ MongoDB not available, skipping RAG context retrieval")
            return None
        
        try:
            # Extract intent from current query
            current_intent = self._extract_query_intent(current_query)
            
            # Build MongoDB query to find relevant past queries
            cutoff_date = datetime.now() - timedelta(days=self.recent_days)
            
            # Query filters
            filters = {
                "createdAt": {"$gte": cutoff_date},
                "sqlQuery": {"$exists": True, "$ne": None},
                "summary": {"$exists": True, "$ne": None}
            }
            
            # Try to match similar database if provided
            if database_config and database_config.get('dbname'):
                # Note: This assumes database name might be stored in some field
                # Adjust based on your actual schema
                pass
            
            # Retrieve recent successful queries
            past_queries = list(self.query_collection.find(
                filters,
                {
                    "requestQuery": 1,
                    "sqlQuery": 1, 
                    "summary": 1,
                    "sqlResponse": 1,
                    "title": 1,
                    "createdAt": 1
                }
            ).sort("createdAt", -1).limit(50))  # Get more to filter better
            
            if not past_queries:
                self.logger.info("🔍 No past queries found for RAG context")
                return None
            
            # Calculate similarity scores and filter relevant queries
            relevant_queries = []
            
            for past_query in past_queries:
                if not past_query.get('requestQuery'):
                    continue
                
                similarity = self._calculate_similarity(
                    current_query, 
                    past_query['requestQuery']
                )
                
                if similarity >= self.similarity_threshold:
                    past_query['similarity_score'] = similarity
                    relevant_queries.append(past_query)
            
            # Sort by similarity and take top matches
            relevant_queries.sort(key=lambda x: x['similarity_score'], reverse=True)
            top_matches = relevant_queries[:self.max_context_queries]
            
            if not top_matches:
                self.logger.info(f"🔍 No relevant queries found (threshold: {self.similarity_threshold})")
                return None
            
            # Build context object
            context = {
                "relevant_queries": [],
                "patterns": self._extract_patterns(top_matches),
                "retrieval_info": {
                    "total_candidates": len(past_queries),
                    "relevant_found": len(top_matches),
                    "avg_similarity": sum(q['similarity_score'] for q in top_matches) / len(top_matches),
                    "threshold_used": self.similarity_threshold
                }
            }
            
            # Format relevant queries for context
            for query in top_matches:
                context["relevant_queries"].append({
                    "original_query": query['requestQuery'],
                    "sql_generated": query.get('sqlQuery', ''),
                    "summary": query.get('summary', ''),
                    "title": query.get('title', ''),
                    "similarity": round(query['similarity_score'], 3),
                    "had_results": bool(query.get('sqlResponse'))
                })
            
            self.logger.info(f"✅ Retrieved {len(top_matches)} relevant queries for RAG context")
            return context
            
        except Exception as e:
            self.logger.error(f"❌ Error retrieving RAG context: {e}")
            return None
    
    def _extract_patterns(self, queries: List[Dict]) -> Dict[str, Any]:
        """Extract common patterns from relevant queries"""
        patterns = {
            "common_tables": [],
            "common_operations": [],
            "typical_filters": []
        }
        
        try:
            # Extract common SQL patterns
            sql_queries = [q.get('sqlQuery', '') for q in queries if q.get('sqlQuery')]
            
            # Find common table names
            tables = []
            for sql in sql_queries:
                # Simple regex to extract table names after FROM and JOIN
                table_matches = re.findall(r'(?:FROM|JOIN)\s+(\w+)', sql, re.IGNORECASE)
                tables.extend(table_matches)
            
            # Count frequency and get most common
            if tables:
                table_counts = {}
                for table in tables:
                    table_counts[table] = table_counts.get(table, 0) + 1
                
                patterns["common_tables"] = [
                    table for table, count in sorted(table_counts.items(), 
                    key=lambda x: x[1], reverse=True)[:3]
                ]
            
            # Extract common operations
            operations = []
            for sql in sql_queries:
                if 'COUNT' in sql.upper():
                    operations.append('COUNT')
                if 'SUM' in sql.upper():
                    operations.append('SUM')
                if 'AVG' in sql.upper():
                    operations.append('AVG')
                if 'GROUP BY' in sql.upper():
                    operations.append('GROUP BY')
                if 'ORDER BY' in sql.upper():
                    operations.append('ORDER BY')
            
            patterns["common_operations"] = list(set(operations))
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error extracting patterns: {e}")
        
        return patterns
    
    def build_enhanced_prompt(self, original_query: str, context: Dict[str, Any]) -> str:
        """
        Build an enhanced prompt that includes RAG context
        
        Args:
            original_query: The user's original query
            context: Retrieved context from query history
            
        Returns:
            Enhanced prompt string with context
        """
        if not context or not context.get('relevant_queries'):
            return original_query
        
        # Build context section
        context_section = "RELEVANT CONTEXT FROM PAST QUERIES:\n\n"
        
        for i, query_ctx in enumerate(context['relevant_queries'][:3], 1):
            context_section += f"Example {i} (similarity: {query_ctx['similarity']}):\n"
            context_section += f"  Question: \"{query_ctx['original_query']}\"\n"
            context_section += f"  SQL: {query_ctx['sql_generated']}\n"
            context_section += f"  Result: {query_ctx['summary']}\n\n"
        
        # Add patterns if available
        if context.get('patterns'):
            patterns = context['patterns']
            if patterns.get('common_tables'):
                context_section += f"Common tables used: {', '.join(patterns['common_tables'])}\n"
            if patterns.get('common_operations'):
                context_section += f"Common operations: {', '.join(patterns['common_operations'])}\n"
            context_section += "\n"
        
        # Build enhanced prompt
        enhanced_prompt = f"""You are an expert SQL assistant with access to relevant examples from past successful queries.

{context_section}

Based on the context above and your expertise, please answer the following query:
"{original_query}"

Generate a SQL query that follows similar patterns to the examples provided while addressing the specific requirements of the current question. Use the same database structure and naming conventions shown in the examples."""

        return enhanced_prompt
    
    def store_query_feedback(self, query: str, sql: str, success: bool, user_feedback: Optional[str] = None):
        """
        Store feedback about query success for future RAG improvements
        This is optional and can be used to improve RAG over time
        """
        if self.query_collection is None:
            return
        
        try:
            feedback_doc = {
                "query": query,
                "sql": sql,
                "success": success,
                "user_feedback": user_feedback,
                "timestamp": datetime.now(),
                "rag_metadata": True  # Flag to identify RAG feedback
            }
            
            # Store in a feedback collection (optional)
            feedback_collection = self.db["rag_feedback"]
            feedback_collection.insert_one(feedback_doc)
            
        except Exception as e:
            self.logger.warning(f"⚠️ Could not store RAG feedback: {e}")
    
    def get_rag_stats(self) -> Dict[str, Any]:
        """Get statistics about RAG usage and effectiveness"""
        if self.query_collection is None:
            return {"status": "MongoDB not available"}
        
        try:
            total_queries = self.query_collection.count_documents({})
            recent_queries = self.query_collection.count_documents({
                "createdAt": {"$gte": datetime.now() - timedelta(days=self.recent_days)}
            })
            
            return {
                "total_queries_in_history": total_queries,
                "recent_queries": recent_queries,
                "similarity_threshold": self.similarity_threshold,
                "max_context_queries": self.max_context_queries,
                "mongodb_connected": True
            }
            
        except Exception as e:
            return {"error": str(e), "mongodb_connected": False}

# Global RAG service instance
_rag_service = None

def get_rag_service() -> RAGService:
    """Get or create global RAG service instance"""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service
