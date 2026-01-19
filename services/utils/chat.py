from fastapi import HTTPException
from langchain_groq import ChatGroq
from utils.db import configure_db, extract_sql_query, is_valid_sql
from utils.rag_service import get_rag_service
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from sqlalchemy import text
import json
from dotenv import load_dotenv
import os
from langchain_core.callbacks.base import BaseCallbackHandler
import io
import sys
from pydantic import SecretStr
import re
from typing import Dict, Any

load_dotenv()
groq_api_key_5 = os.getenv("GROQ_API_KEY_1")

# Custom callback handler to capture agent's thought process
class CaptureStdoutCallbackHandler(BaseCallbackHandler):
    def __init__(self):
        self.thought_process = io.StringIO()
        self.stdout_backup = sys.stdout
        
    def start_capturing(self):
        sys.stdout = self.thought_process
        
    def stop_capturing(self):
        sys.stdout = self.stdout_backup
        
    def get_output(self):
        return self.thought_process.getvalue()

def extract_sql_from_response(response_text: str) -> str:
    """
    Extract SQL query from agent response text.
    Handles cases where the agent returns the query directly or wrapped in markdown.
    """
    # Try to extract SQL from markdown code blocks
    sql_match = re.search(r"```sql\s*(.*?)\s*```", response_text, re.DOTALL | re.IGNORECASE)
    if sql_match:
        return sql_match.group(1).strip()
    
    # Try to extract SQL from generic code blocks
    sql_match = re.search(r"```\s*(.*?)\s*```", response_text, re.DOTALL)
    if sql_match:
        return sql_match.group(1).strip()
    
    # If no code blocks found, look for SQL-like patterns
    sql_patterns = [
        r"(SELECT\s+.*?FROM\s+.*?WHERE\s+.*?;)",
        r"(SELECT\s+.*?FROM\s+.*?;)",
        r"(SELECT\s+.*?;)"
    ]
    
    for pattern in sql_patterns:
        sql_match = re.search(pattern, response_text, re.DOTALL | re.IGNORECASE)
        if sql_match:
            return sql_match.group(1).strip()
    
    # If all else fails, return the text as is (might be the SQL query)
    return response_text.strip()

def process_database_query(db_name, host, user, password, database, query, llm, engine, db, database_config=None):
    """Helper function to process database queries for both PostgreSQL and MySQL with RAG enhancement"""
    
    # Initialize RAG service
    rag_service = get_rag_service()
    
    # Try to retrieve relevant context from query history
    rag_context = None
    enhanced_query = query
    
    try:
        rag_context = rag_service.retrieve_relevant_context(query, database_config or {})
        if rag_context:
            enhanced_query = rag_service.build_enhanced_prompt(query, rag_context)
            print(f"✅ RAG: Enhanced query with {len(rag_context['relevant_queries'])} relevant examples")
        else:
            print("🔍 RAG: No relevant context found, proceeding without enhancement")
    except Exception as e:
        print(f"⚠️ RAG: Context retrieval failed ({e}), proceeding without enhancement")
    
    # Setup to capture agent's thought process
    capture_handler = CaptureStdoutCallbackHandler()
    capture_handler.start_capturing()
   
    try:
        toolkit = SQLDatabaseToolkit(db=db, llm=llm)
        
        # Create agent with enhanced error handling
        agent = create_sql_agent(
            llm=llm,
            toolkit=toolkit,
            verbose=True,
            agent_type="zero-shot-react-description",
            handle_parsing_errors=True,
            max_iterations=10,
            early_stopping_method="force",
            return_intermediate_steps=True
        )
        
        # Adjust prompt based on database type
        if db_name == "postgresql":
            db_version = "PostgreSQL"
        elif db_name == "mysql":
            db_version = "MySQL 8.0"
        else:
            db_version = db_name
            
        # Use enhanced query if RAG context is available
        base_query = enhanced_query if rag_context else query
            
        sql_generation_prompt = f"""
        For the following question, generate a valid SQL query to answer it.
        Question: "{base_query}"
        
        You must return a valid SQL query that would run in {db_version}.
        The query should only start with SELECT (read-only operation).
        If you cannot find the answer, return "SELECT NULL LIMIT 0" as the query.
        DO NOT include explanations, markdown formatting, or anything else - ONLY the SQL query itself.
        
        Important for {db_version}:
        - Use proper {db_version} syntax and functions
        - Be aware of {db_version} specific features and limitations
        - Use appropriate quoting for table/column names if they contain special characters
        - Follow {db_version} date/time function syntax
        """
        
        # Run the agent with better error handling
        try:
            agent_response = agent.invoke({"input": sql_generation_prompt})
            
            # Extract the output from the invoke response
            if isinstance(agent_response, dict):
                if "output" in agent_response:
                    agent_output = agent_response["output"]
                elif "result" in agent_response:
                    agent_output = agent_response["result"]
                else:
                    # Try to get the first value that looks like output
                    for key, value in agent_response.items():
                        if isinstance(value, str) and ("SELECT" in value.upper() or "FROM" in value.upper()):
                            agent_output = value
                            break
                    else:
                        agent_output = str(agent_response)
            else:
                agent_output = str(agent_response)
                
        except Exception as agent_error:
            # Fallback to run method without additional arguments
            try:
                agent_output = agent.run(sql_generation_prompt)
            except Exception as run_error:
                # If both methods fail, provide a more helpful error
                raise ValueError(f"Agent execution failed: {str(run_error)}. Original error: {str(agent_error)}")
       
        # Capture output and restore stdout
        thought_process = capture_handler.get_output()
        capture_handler.stop_capturing()
        
        # Extract and validate SQL query
        sql_query = extract_sql_from_response(agent_output)
        
        # If the agent returned an error message or "I don't know", handle it
        if "i don't know" in sql_query.lower() or "don't know" in sql_query.lower():
            sql_query = "SELECT NULL LIMIT 0"
        
        if not is_valid_sql(sql_query):
            # Try to extract SQL one more time with different method
            sql_query = extract_sql_query(agent_output)
            if not is_valid_sql(sql_query):
                # If still not valid, create a simple query
                sql_query = f"SELECT * FROM information_schema.tables LIMIT 5"
        
        # Execute the SQL query with error handling
        sql_result_list = []
        try:
            with engine.connect() as connection:
                result = connection.execute(text(sql_query))
                if result.returns_rows:
                    columns = result.keys()
                    for row in result:
                        row_dict = {col: value for col, value in zip(columns, row)}
                        for key, value in row_dict.items():
                            if not isinstance(value, (str, int, float, bool, type(None))):
                                row_dict[key] = str(value)
                        sql_result_list.append(row_dict)
                    sql_result_str = json.dumps(sql_result_list)
                else:
                    sql_result_str = "Query executed successfully. No rows returned."
        except Exception as sql_error:
            # If SQL execution fails, provide error details
            sql_result_str = f"SQL execution error: {str(sql_error)}"
            sql_result_list = []
        
        # Generate summary with enhanced prompt for better insights
        if sql_result_list and len(sql_result_list) > 0:
            # Successful query with results
            summary_prompt = f"""
            Based on the following database query and results, provide a smart, concise summary (2-3 sentences) that highlights the most relevant insights:
            
            Question: {query}
            SQL Query: {sql_query}
            SQL Results: {sql_result_str}
            
            Focus on:
            - Key findings and patterns in the data
            - Notable trends, highest/lowest values, or standout metrics
            - Actionable insights from the results
            
            Provide a clear, contextual summary that explains what these results mean in practical terms.
            """
            summary = llm.invoke(summary_prompt).content
        elif "SQL execution error:" in sql_result_str:
            # SQL execution failed
            summary = "The query encountered an error during execution. Please check the query syntax and try again."
        else:
            # Query executed successfully but returned no results
            summary = "No matching records were found for your query."
        
        # Generate title with enhanced prompt
        if sql_result_list and len(sql_result_list) > 0:
            title_prompt = f"""
            Based on the following question and results, create a brief, descriptive title (5-8 words):
            
            Question: {query}
            SQL Results: {sql_result_str}
            
            Create a concise title that captures the key finding or main topic of the query results.
            Focus on what was discovered, not just what was asked.
            """
            title = llm.invoke(title_prompt).content
        elif "SQL execution error:" in sql_result_str:
            title = "Query Execution Error"
        else:
            title = "No Results Found"
        
        # Prepare response with RAG metadata (optional, for debugging)
        response = {
            "user_query": query,
            "sql_query": sql_query,
            "sql_result": sql_result_list if sql_result_list else sql_result_str,
            "summary": summary,
            "title": title,
            "agent_thought_process": thought_process
        }
        
        # Add RAG metadata if context was used (optional for debugging)
        if rag_context:
            response["rag_metadata"] = {
                "context_used": True,
                "relevant_examples": len(rag_context['relevant_queries']),
                "avg_similarity": rag_context['retrieval_info']['avg_similarity']
            }
        
        return response
        
    except Exception as e:
        # Ensure stdout is restored even if an error occurs
        capture_handler.stop_capturing()
        raise e

def chat_db(db_name, host, user, password, database, query, database_config=None):
    """Main function to handle database chat queries with RAG enhancement"""
    if db_name == "neo4j":
        # Handle Neo4j graph database queries
        from utils.neo4j_chat import chat_neo4j
        return chat_neo4j(db_name, host, user, password, database, query)
    elif db_name not in ["postgresql", "mysql"]:
        raise HTTPException(status_code=400, detail=f"Unsupported database type: {db_name}")
    
    if not groq_api_key_5:
        raise HTTPException(status_code=500, detail="GROQ API key not found in environment variables")
    
    try:
        # Initialize LLM
        llm_api_key = groq_api_key_5 if groq_api_key_5 is not None else ""
        llm = ChatGroq(
            api_key=SecretStr(llm_api_key),
            model="llama-3.3-70b-versatile",  # Start with smaller model
            streaming=False,
            temperature=0.1  # Lower temperature for more deterministic SQL generation
        )
        
        db, engine = configure_db(db_name, host, user, password, database)
        
        return process_database_query(db_name, host, user, password, database, query, llm, engine, db, database_config)
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        error_msg = f"Error processing query: {str(e)}"
        
        # Provide more user-friendly error messages
        if "rate limit" in error_msg.lower() or "quota" in error_msg.lower():
            error_msg += ". Please try again later or check your API quota."
        
        raise HTTPException(status_code=500, detail=f"{error_msg}\n{error_details}")