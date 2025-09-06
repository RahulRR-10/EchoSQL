from fastapi import HTTPException
from langchain_groq import ChatGroq
from utils.db import configure_db, get_database_schema
from neo4j import GraphDatabase, Driver
import json
from dotenv import load_dotenv
import os
from pydantic import SecretStr
import re
from typing import Dict, Any, Union

load_dotenv()
groq_api_key_5 = os.getenv("GROQ_API_KEY_1")

def format_neo4j_results(result_records):
    """Format Neo4j results into user-friendly display format"""
    if not result_records:
        return []
    
    formatted_results = []
    
    for record in result_records:
        formatted_record = {}
        
        for key, value in record.items():
            if isinstance(value, dict) and '_labels' in value:
                # This is a Neo4j node - format it nicely
                node_type = value.get('_labels', ['Unknown'])[0]
                formatted_node = {
                    'type': node_type,
                    'properties': {}
                }
                
                # Extract and format key properties
                for prop_key, prop_value in value.items():
                    if prop_key != '_labels':
                        if prop_key == 'annual_revenue' and isinstance(prop_value, (int, float)):
                            # Format large numbers
                            formatted_node['properties'][prop_key] = f"${prop_value:,.0f}"
                        elif prop_key == 'customer_base' and isinstance(prop_value, (int, float)):
                            formatted_node['properties'][prop_key] = f"{prop_value:,} customers"
                        elif prop_key == 'market_share' and isinstance(prop_value, float):
                            formatted_node['properties'][prop_key] = f"{prop_value:.1%}"
                        elif prop_key == 'stores' and isinstance(prop_value, (int, float)):
                            formatted_node['properties'][prop_key] = f"{prop_value:,} stores"
                        else:
                            formatted_node['properties'][prop_key] = prop_value
                
                formatted_record[key] = formatted_node
            elif isinstance(value, dict) and '_type' in value:
                # This is a Neo4j relationship - format it nicely  
                rel_type = value.get('_type', 'Unknown')
                formatted_rel = {
                    'type': f"Relationship: {rel_type}",
                    'properties': {k: v for k, v in value.items() if k != '_type'}
                }
                formatted_record[key] = formatted_rel
            else:
                # This is a primitive value
                formatted_record[key] = value
        
        formatted_results.append(formatted_record)
    
    return formatted_results

def process_neo4j_query(db_name, host, user, password, database, query, llm, driver):
    """Process Neo4j graph database queries using Cypher"""
    
    try:
        # Get graph schema
        schema = get_database_schema(None, "neo4j", driver)
        
        # Create Cypher generation prompt
        cypher_prompt = f"""
        You are an expert Neo4j Cypher query generator. Given the following graph schema and user question, 
        generate a valid Cypher query to answer it.
        
        Graph Schema:
        Node Labels: {list(schema['nodes'].keys())}
        Node Properties: {json.dumps(schema['nodes'], indent=2)}
        Relationship Types: {list(schema['relationships'].keys())}
        
        User Question: "{query}"
        
        Important rules:
        1. ONLY return a valid Cypher query - no explanations or markdown
        2. Use MATCH, WHERE, RETURN appropriately
        3. Limit results to 20 unless specifically asked for more
        4. Use appropriate aggregation functions when needed
        5. For store queries, focus on Customer, Product, Order, Category nodes
        6. Common patterns:
           - Find products: MATCH (p:Product) WHERE ... RETURN p
           - Find customers: MATCH (c:Customer) WHERE ... RETURN c
           - Find orders: MATCH (c:Customer)-[:PLACED]->(o:Order) WHERE ... RETURN o, c
           - Product relationships: MATCH (p:Product)-[:BELONGS_TO]->(cat:Category)
        
        Generate only the Cypher query:
        """
        
        # Generate Cypher query using LLM
        cypher_response = llm.invoke(cypher_prompt)
        cypher_query = cypher_response.content.strip()
        
        # Generate thought process for Neo4j query
        thought_process_prompt = f"""
        Explain the reasoning behind this Neo4j Cypher query in a clear, step-by-step manner:
        
        User Question: "{query}"
        Generated Cypher: {cypher_query}
        Available Schema: {list(schema['nodes'].keys())} nodes, {list(schema['relationships'].keys())} relationships
        
        Provide a brief explanation of:
        1. What graph patterns are being matched
        2. Why this approach was chosen
        3. What the query will return
        
        Keep it concise and technical but understandable.
        """
        
        thought_process_response = llm.invoke(thought_process_prompt)
        thought_process = thought_process_response.content.strip()
        
        # Clean up the query (remove markdown if present)
        cypher_query = re.sub(r'```cypher\s*', '', cypher_query)
        cypher_query = re.sub(r'```\s*', '', cypher_query)
        cypher_query = cypher_query.strip()
        
        # Execute Cypher query
        result_records = []
        with driver.session() as session:
            result = session.run(cypher_query)
            
            for record in result:
                # Convert record to dictionary
                record_dict = {}
                for key in record.keys():
                    value = record[key]
                    
                    # Handle Neo4j node/relationship objects
                    if hasattr(value, '_properties') and hasattr(value, '_labels'):
                        # It's a Neo4j node - extract properties
                        node_data = dict(value._properties)
                        node_data['_labels'] = list(value._labels)
                        record_dict[key] = node_data
                    elif hasattr(value, '_properties') and hasattr(value, '_type'):
                        # It's a Neo4j relationship - extract properties
                        rel_data = dict(value._properties)
                        rel_data['_type'] = value._type
                        record_dict[key] = rel_data
                    else:
                        # It's a primitive value (string, number, etc.)
                        record_dict[key] = value
                
                result_records.append(record_dict)
                
        print(f"[DEBUG] Neo4j result_records: {result_records[:3]}")  # Debug first 3 records
        
        # Format results for better display
        formatted_results = format_neo4j_results(result_records)
        
        # Generate summary using formatted results for better readability
        if formatted_results:
            # Use formatted results for summary but limit the data shown
            summary_data = []
            for record in formatted_results[:3]:  # Only use first 3 for summary
                summary_item = {}
                for key, value in record.items():
                    if isinstance(value, dict) and 'type' in value:
                        # Extract key properties for summary
                        node_type = value['type']
                        props = value.get('properties', {})
                        key_props = {}
                        
                        # Include most relevant properties
                        important_props = ['name', 'location', 'type', 'annual_revenue', 'customer_base', 'market_share']
                        for prop in important_props:
                            if prop in props:
                                key_props[prop] = props[prop]
                        
                        summary_item[key] = f"{node_type}: {key_props}"
                    else:
                        summary_item[key] = value
                summary_data.append(summary_item)
            
            summary_prompt = f"""
            Based on the following Neo4j graph query and results, provide a concise summary (2-3 sentences):
            
            User Question: {query}
            Cypher Query: {cypher_query}
            Sample Results: {json.dumps(summary_data, indent=2)}
            Total Records: {len(result_records)}
            
            Focus on the key insights and findings from the graph data.
            """
            
            summary = llm.invoke(summary_prompt).content
        else:
            summary = "No matching records found in the graph database for your query."
        
        # Generate title
        if result_records:
            title_prompt = f"""
            Create a brief, descriptive title (5-8 words) for this graph query result:
            Question: {query}
            Results found: {len(result_records)} records
            
            Focus on what was discovered in the graph.
            """
            title = llm.invoke(title_prompt).content.strip()
        else:
            title = "No Graph Results Found"
        
        result = {
            "user_query": query,
            "cypher_query": cypher_query,
            "graph_result": formatted_results,  # Use formatted results instead of raw
            "summary": summary,
            "title": title,
            "database_type": "neo4j",
            "agent_thought_process": thought_process
        }
        
        print(f"[DEBUG] Final Neo4j result structure: user_query={result['user_query']}, cypher_query={result['cypher_query']}, graph_result_count={len(result['graph_result'])}, summary={result['summary'][:50]}...")
        
        return result
        
    except Exception as e:
        error_msg = f"Graph query error: {str(e)}"
        error_thought_process = f"Attempted to process Neo4j query: '{query}'. Error occurred during query generation or execution: {str(e)}"
        return {
            "user_query": query,
            "cypher_query": cypher_query if 'cypher_query' in locals() else "Query generation failed",
            "graph_result": [],
            "summary": error_msg,
            "title": "Graph Query Error",
            "database_type": "neo4j",
            "agent_thought_process": error_thought_process
        }

def chat_neo4j(db_name, host, user, password, database, query):
    """Main function to handle Neo4j graph database queries"""
    
    print(f"[DEBUG] chat_neo4j called with: db_name={db_name}, host={host}, user={user}, database={database}, query={query}")
    
    if not groq_api_key_5:
        print(f"[ERROR] GROQ API key not found: {groq_api_key_5}")
        raise HTTPException(status_code=500, detail="GROQ API key not found in environment variables")
    
    print(f"[DEBUG] GROQ API key found: {groq_api_key_5[:10]}...")
    
    try:
        # Initialize LLM
        print("[DEBUG] Initializing LLM...")
        llm = ChatGroq(
            api_key=SecretStr(groq_api_key_5),
            model="llama-3.3-70b-versatile",
            streaming=False,
            temperature=0.1
        )
        print("[DEBUG] LLM initialized successfully")
        
        # Connect to Neo4j
        print(f"[DEBUG] Connecting to Neo4j with host: {host}")
        db_connection, _ = configure_db(db_name, host, user, password, database)
        print(f"[DEBUG] Neo4j connection established: {type(db_connection)}")
        
        # For Neo4j, the connection should be a Driver
        if not hasattr(db_connection, 'session'):
            raise HTTPException(status_code=500, detail="Invalid Neo4j connection returned")
        
        print("[DEBUG] Calling process_neo4j_query...")
        result = process_neo4j_query(db_name, host, user, password, database, query, llm, db_connection)
        print(f"[DEBUG] process_neo4j_query returned: {type(result)}")
        
        # Close Neo4j driver safely
        try:
            if db_connection and hasattr(db_connection, 'close'):
                getattr(db_connection, 'close')()  # Use getattr to avoid IDE type confusion
        except Exception as e:
            print(f"Warning: Error closing Neo4j driver: {e}")
        
        print(f"[DEBUG] Final result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        return result
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        error_msg = f"Error processing Neo4j query: {str(e)}"
        print(f"[ERROR] Exception in chat_neo4j: {error_msg}")
        print(f"[ERROR] Traceback: {error_details}")
        
        raise HTTPException(status_code=500, detail=f"{error_msg}\n{error_details}")
