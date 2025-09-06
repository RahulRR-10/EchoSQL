#!/usr/bin/env python3
"""
Test Neo4j integration with Aura
"""

import sys
import os
sys.path.append('services')

from utils.neo4j_chat import chat_neo4j

def test_neo4j_integration():
    print("🧪 Testing Neo4j Integration...")
    print("=" * 50)
    
    # Connection details
    uri = "neo4j://127.0.0.1:7687"
    username = "neo4j"
    password = "password"
    database = "neo4j"
    
    # Test queries
    test_queries = [
        "Show me all product categories",
        "Who are the top 5 customers by total spending?",
        "What are the highest rated products?",
        "Find customers from New York",
        "Show me recent orders"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Test {i}: {query}")
        print("-" * 40)
        
        try:
            result = chat_neo4j("neo4j", uri, username, password, database, query)
            
            print(f"✅ Title: {result['title']}")
            print(f"🔗 Cypher: {result['cypher_query']}")
            print(f"📊 Results: {len(result['graph_result'])} records")
            print(f"📝 Summary: {result['summary'][:100]}...")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    print(f"\n✅ Neo4j integration test completed!")

if __name__ == "__main__":
    test_neo4j_integration()
