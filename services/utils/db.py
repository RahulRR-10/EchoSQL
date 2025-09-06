import re
from fastapi import HTTPException
from sqlalchemy import create_engine, inspect
from langchain_community.utilities import SQLDatabase
from neo4j import GraphDatabase


def configure_db(db_name, host, user, password, database):
    if db_name == "mysql": 
        try:
            from urllib.parse import quote_plus
            safe_password = quote_plus(password)
            conn_string = f"mysql+mysqlconnector://{user}:{safe_password}@{host}/{database}"
            engine = create_engine(conn_string)
            return SQLDatabase(engine), engine
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")
    elif db_name == "postgresql":
        try:
            conn_string = f"postgresql+psycopg2://{user}:{password}@{host}/{database}"
            engine = create_engine(conn_string, connect_args={"options": "-c default_transaction_read_only=on"})
            return SQLDatabase(engine), engine
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")
    elif db_name == "neo4j":
        try:
            # For Neo4j, host is the full URI (e.g., neo4j://127.0.0.1:7687)
            driver = GraphDatabase.driver(host, auth=(user, password))
            # Test the connection
            with driver.session() as session:
                session.run("RETURN 1")
            return driver, None  # Return driver and None for engine (not applicable to Neo4j)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Neo4j connection error: {str(e)}")
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported database type: {db_name}. Choose 'mysql', 'postgresql', or 'neo4j'.")
    
def get_database_schema(engine, db_type="sql", driver=None):
    if db_type == "neo4j" and driver:
        return get_neo4j_schema(driver)
    else:
        # Original SQL schema logic
        inspector = inspect(engine)
        schema = {}
        tables = inspector.get_table_names()
        for table in tables:
            columns = inspector.get_columns(table)
            schema[table] = [col['name'] for col in columns]
        return schema

def get_neo4j_schema(driver):
    """Get Neo4j database schema including nodes and relationships"""
    schema = {
        "nodes": {},
        "relationships": {},
        "sample_queries": []
    }
    
    try:
        with driver.session() as session:
            # Get node labels and their properties
            result = session.run("""
                CALL db.labels() YIELD label
                RETURN label
            """)
            
            for record in result:
                label = record["label"]
                
                # Get properties for this label
                props_result = session.run(f"""
                    MATCH (n:{label})
                    RETURN keys(n) as properties
                    LIMIT 1
                """)
                
                properties = []
                for prop_record in props_result:
                    if prop_record["properties"]:
                        properties = prop_record["properties"]
                        break
                
                schema["nodes"][label] = properties
            
            # Get relationship types
            rel_result = session.run("""
                CALL db.relationshipTypes() YIELD relationshipType
                RETURN relationshipType
            """)
            
            for record in rel_result:
                rel_type = record["relationshipType"]
                schema["relationships"][rel_type] = []
            
            # Add sample queries based on our store data
            schema["sample_queries"] = [
                "Find all customers from New York",
                "Show products with rating above 4.5",
                "What are the most popular product categories?",
                "Find customers who bought electronics",
                "Show orders placed in the last 30 days",
                "Which products have the most reviews?",
                "Find customers with highest total spending",
                "Show product recommendations for a customer"
            ]
            
    except Exception as e:
        print(f"Error getting Neo4j schema: {e}")
    
    return schema
    
def extract_sql_query(agent_response):
    if re.match(r'^[\d.]+$', agent_response.strip()):
        raise ValueError(f"Agent returned a numeric value instead of SQL: {agent_response}")

    sql_match = re.search(r'```sql\s*(.*?)\s*```', agent_response, re.DOTALL)
    if sql_match:
        return sql_match.group(1).strip()

    sql_match = re.search(r'`(.*?)`', agent_response, re.DOTALL)
    if sql_match:
        return sql_match.group(1).strip()

    sql_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'ALTER', 'DROP', 'SHOW']
    for keyword in sql_keywords:
        sql_match = re.search(f'{keyword}\\s+.*', agent_response, re.IGNORECASE | re.DOTALL)
        if sql_match:
            return sql_match.group(0).strip()

    if any(keyword in agent_response.upper() for keyword in sql_keywords):
        return agent_response.strip()

    raise ValueError(f"Could not identify SQL query in agent response: {agent_response}")
    
def is_valid_sql(query):
    if re.match(r'^[\d.]+$', query.strip()):
        return False

    if not query.upper().strip().startswith('SELECT'):
        return False

    select_keywords = ['SELECT', 'FROM', 'WHERE', 'JOIN', 'GROUP BY', 'ORDER BY', 'HAVING', 'LIMIT']
    return any(keyword.upper() in query.upper() for keyword in select_keywords)


def generate_natural_language_queries(schema):
    """Generate a list of possible natural language queries based on the schema."""
    queries = []
    
    for table, columns in schema.items():
        
        queries.append(f"What are the details of all records in the '{table}' table?")
        queries.append(f"Show me all {', '.join(columns)} from the '{table}' table.")
        
        for column in columns:
            queries.append(f"Give me the {column} from the '{table}' table.")
            
        if len(columns) > 1:
            queries.append(f"What is the average {columns[0]} in the '{table}' table?")
            queries.append(f"How many records are there in the '{table}' table?")
        
    return queries

