#!/usr/bin/env python3
"""
RAG Implementation Demo Script
This script demonstrates how the RAG system works with your existing query history.
"""

import json
from utils.rag_service import get_rag_service
from utils.chat import chat_db
import os
from dotenv import load_dotenv

load_dotenv()

def test_rag_implementation():
    """Test the RAG implementation with sample queries"""
    
    print("🔥 RAG (Retrieval-Augmented Generation) Implementation Demo")
    print("=" * 60)
    
    # Initialize RAG service
    rag_service = get_rag_service()
    
    # Check RAG service status
    print("\n📊 RAG Service Status:")
    stats = rag_service.get_rag_stats()
    print(json.dumps(stats, indent=2))
    
    # Test sample queries
    test_queries = [
        "Show me all customers",
        "What are the top products by price?", 
        "Count total orders",
        "Find customers from California"
    ]
    
    # Sample database config (you can modify this to match your test database)
    db_config = {
        "dbtype": "mysql",
        "host": "localhost",
        "user": "root",
        "password": "password",
        "dbname": "bigstore_db"
    }
    
    print(f"\n🧪 Testing RAG Context Retrieval:")
    print("-" * 40)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: '{query}'")
        
        # Test RAG context retrieval
        context = rag_service.retrieve_relevant_context(query, db_config)
        
        if context:
            print(f"   ✅ RAG Context Found:")
            print(f"   📋 Relevant examples: {len(context['relevant_queries'])}")
            print(f"   📈 Average similarity: {context['retrieval_info']['avg_similarity']:.3f}")
            
            # Show enhanced prompt (first 200 chars)
            enhanced_prompt = rag_service.build_enhanced_prompt(query, context)
            preview = enhanced_prompt[:200] + "..." if len(enhanced_prompt) > 200 else enhanced_prompt
            print(f"   💡 Enhanced prompt preview: {preview}")
            
        else:
            print(f"   🔍 No relevant context found (this is normal for new systems)")
    
    print(f"\n🎯 Key Features Implemented:")
    print("  ✅ Automatic context retrieval from MongoDB query history")
    print("  ✅ Semantic similarity matching between queries")
    print("  ✅ Enhanced prompt generation with relevant examples")
    print("  ✅ Graceful fallback when no context is available")
    print("  ✅ Transparent to end users (no UI changes needed)")
    
    print(f"\n🔧 Configuration:")
    print(f"  • Similarity threshold: {rag_service.similarity_threshold}")
    print(f"  • Max context queries: {rag_service.max_context_queries}")
    print(f"  • Recent days filter: {rag_service.recent_days}")
    
    # Test a complete chat interaction (if database is available)
    print(f"\n🚀 Testing Complete RAG-Enhanced Chat Flow:")
    print("-" * 50)
    
    try:
        # This would be a real query to your database
        test_query = "Show me all products"
        print(f"Query: '{test_query}'")
        
        # This will use RAG internally if context is available
        # result = chat_db(
        #     db_config["dbtype"], 
        #     db_config["host"], 
        #     db_config["user"],
        #     db_config["password"], 
        #     db_config["dbname"], 
        #     test_query,
        #     db_config
        # )
        # print(f"Result: {json.dumps(result, indent=2)}")
        print("   💬 (Chat test skipped - requires database connection)")
        
    except Exception as e:
        print(f"   ⚠️ Chat test failed: {e}")
        print("   💡 This is expected if database is not set up")
    
    print(f"\n🎉 RAG Implementation Complete!")
    print("   📝 Users can now ask queries as usual")
    print("   🧠 System automatically enhances responses with relevant context")
    print("   🔄 No UI changes required - RAG works transparently")

if __name__ == "__main__":
    test_rag_implementation()
