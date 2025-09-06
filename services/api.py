from fastapi import FastAPI, HTTPException, UploadFile, Form, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
from utils.db import configure_db, get_database_schema
from utils.chat import chat_db
from groq import Groq
# Using requests for simple translation instead of googletrans
import os
from dotenv import load_dotenv
from pathlib import Path
import uuid
from fastapi.responses import FileResponse
from typing import Optional, List, Dict, Any
import json
import re
import traceback
import requests
from twilio.twiml.messaging_response import MessagingResponse

load_dotenv()


groq_api_key_2 = os.getenv("GROQ_API_KEY_2")

if not groq_api_key_2:
    print("Warning: GROQ_API_KEY_2 environment variable not set. Please set it in your .env file or environment.")
    print("You can create a .env file in the services directory with: GROQ_API_KEY_2=your_api_key_here")
    groq_api_key_2 = "dummy_key_for_development"  # Fallback for development

api = FastAPI()
client = Groq(api_key=groq_api_key_2)

# Add CORS middleware
api.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Allow only local development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
client = Groq(api_key=groq_api_key_2)

class DatabaseConfig(BaseModel):
    dbtype: str
    host: str
    user: str
    password: str
    dbname: str
    uri: Optional[str] = None  # For Neo4j connections
    
class QueryRequest(BaseModel):
    query: str

class SearchCompletionsRequest(BaseModel):
    term: str = Field(..., description="The partial search term to find completions for")
    limit: int = Field(10, description="Maximum number of completions to return")
    database_config: Optional[DatabaseConfig] = None

class GraphRecommendationRequest(BaseModel):
    sql_result_json: List[Dict[str, Any]] = Field(..., description="The result of the SQL query in JSON format (list of dictionaries)")

async def translate_to_english(text: str) -> str:
    # Since googletrans is not available, we'll use the Groq model for translation
    # This is a simple alternative that doesn't require additional dependencies
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a translation assistant. Translate the given text to English."},
                {"role": "user", "content": f"Translate this text to English: {text}"}
            ],
            model="llama-3.1-8b-instant",
            temperature=0.3,
            max_tokens=256
        )
        translated_text = response.choices[0].message.content
        if translated_text:
            return translated_text.strip()
        return text  # Return original text if translation fails
    except Exception as e:
        print(f"Translation error: {e}")
        return text  # Return original text if translation fails

@api.get("/")  
def read_root():   
    return {"Hello": "World"}


@api.post("/chat")
async def chat_with_db(request_data: dict):
    print(f"[DEBUG] Incoming /chat payload: {json.dumps(request_data, indent=2)}")
    
    if "database_config" not in request_data or "query_request" not in request_data:
        raise HTTPException(status_code=400, detail="Request must include database_config and query_request")
    
    db_config_data = request_data["database_config"]
    query_request_data = request_data["query_request"]
    print(f"[DEBUG] DB config: {db_config_data}")
    print(f"[DEBUG] Query request: {query_request_data}")
    
    try:
        db_config = DatabaseConfig(**db_config_data)    
        query_request = QueryRequest(**query_request_data)
        print(f"[DEBUG] Parsed - dbtype: {db_config.dbtype}, query: {query_request.query}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid request format: {str(e)}")
    
    try:
        # Handle Neo4j URI construction
        if db_config.dbtype == "neo4j":
            if db_config.uri:
                connection_host = db_config.uri
            else:
                # Fallback: construct URI from host
                if "://" in db_config.host:
                    connection_host = db_config.host  # Already a URI
                else:
                    connection_host = f"neo4j://{db_config.host}:7687"  # Construct URI
        else:
            connection_host = db_config.host
        
        db, engine = configure_db(
            db_config.dbtype, connection_host, db_config.user, 
            db_config.password, db_config.dbname
        )
    
        result = chat_db(
            db_config.dbtype, connection_host, db_config.user, 
            db_config.password, db_config.dbname, query_request.query
        )
        
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        return {
            "user_query": query_request.query,
            "error": "This query doesn't appear to be related to the database. Please try again with a database-related question.",
            "details": str(e)
        }

@api.post("/recommend")
async def recommend_queries(request_data: dict):
    import json
    print(f"[DEBUG] Incoming /recommend payload: {json.dumps(request_data, indent=2)}")
    if "database_config" not in request_data:
        print("[ERROR] Missing 'database_config' in payload.")
        raise HTTPException(status_code=400, detail="Request must include database_config")

    data_config_data = request_data["database_config"]
    print(f"[DEBUG] Raw database_config: {data_config_data}")
    try:
        db_config = DatabaseConfig(**data_config_data)
        print(f"[DEBUG] Parsed db_config: {db_config}")
    except Exception as e:
        print(f"[ERROR] Invalid request format: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid request format: {str(e)}")

    try:
        print(f"[DEBUG] Connecting to DB: type={db_config.dbtype}, host={db_config.host}, user={db_config.user}, db={db_config.dbname}")
        
        if db_config.dbtype == "neo4j":
            # Handle Neo4j graph database
            # Use uri field if provided, otherwise construct from host
            if db_config.uri:
                neo4j_uri = db_config.uri
            else:
                # Fallback: construct URI from host
                if "://" in db_config.host:
                    neo4j_uri = db_config.host  # Already a URI
                else:
                    neo4j_uri = f"neo4j://{db_config.host}:7687"  # Construct URI
            
            print(f"[DEBUG] Using Neo4j URI: {neo4j_uri}")
            driver, _ = configure_db(db_config.dbtype, neo4j_uri, db_config.user, db_config.password, db_config.dbname)
            schema = get_database_schema(None, "neo4j", driver)
            
            prompt = f"""
            Given the following Neo4j graph database schema:
            Node Types: {list(schema['nodes'].keys())}
            Node Properties: {json.dumps(schema['nodes'], indent=2)}
            Relationship Types: {list(schema['relationships'].keys())}
            
            Generate 10 natural language questions that a business user might ask about this graph database.
            Focus on relationships, patterns, and insights that can be discovered in the graph.
            Each question should be clear and answerable using Cypher queries.
            
            Return ONLY a JSON array of questions (no Cypher queries, no explanations).
            
            Example format:
            ["Who are my top customers by total spending?", "What products are frequently bought together?", "Which product categories have the highest ratings?"]
            
            Generate 10 similar questions for this schema and return as a JSON array:
            """
            
            # Close Neo4j driver
            try:
                getattr(driver, 'close')()  # type: ignore
            except:
                pass
        else:
            # Handle SQL databases (existing logic)
            _, engine = configure_db(db_config.dbtype, db_config.host, db_config.user, db_config.password, db_config.dbname)
            print("[DEBUG] DB connection successful.")
            schema = get_database_schema(engine)
            print(f"[DEBUG] Retrieved schema: {schema}")
            prompt = f"""
            Given the following database schema:
            {schema}
            
            Generate 10 natural language queries that a business user might ask about this database.
            Each query should be a single sentence and should be relevant to the schema provided.
            Avoid complex queries or technical jargon. The query should be simple and understandable.
            the query should be start with select when coverted to sql query.
            Return them as a JSON array of strings. Each query should be clear and answerable using SQL.
            """
        print(f"[DEBUG] LLM prompt: {prompt}")
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a database expert that helps generate natural language queries."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.1-8b-instant", 
            temperature=0.7,
            max_tokens=1024
        )
        llm_response = response.choices[0].message.content
        print(f"[DEBUG] LLM response: {llm_response}")
        
        recommended_queries = []
        if llm_response:
            try:
                # First try to parse as direct JSON
                recommended_queries = json.loads(llm_response)
            except json.JSONDecodeError:
                try:
                    # Try to find JSON array in the response
                    json_match = re.search(r'\[.*?\]', llm_response, re.DOTALL)
                    if json_match:
                        recommended_queries = json.loads(json_match.group(0))
                    else:
                        # Fallback: extract questions manually
                        lines = llm_response.split('\n')
                        questions = []
                        for line in lines:
                            line = line.strip()
                            # Look for numbered questions or questions in quotes
                            if '"' in line and not line.startswith('-'):
                                # Extract text between quotes
                                quote_match = re.search(r'"([^"]+)"', line)
                                if quote_match:
                                    questions.append(quote_match.group(1))
                            elif line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.')):
                                # Extract question after number
                                question = re.sub(r'^\d+\.\s*', '', line)
                                question = question.strip('"').strip("'").strip()
                                if question and not question.startswith('Cypher'):
                                    questions.append(question)
                        recommended_queries = questions
                except:
                    # Final fallback
                    recommended_queries = [q.strip().strip('"').strip("'") for q in llm_response.split('\n') if q.strip() and not q.strip().startswith('-')]
        print(f"[DEBUG] Recommended queries: {recommended_queries}")
        return {
            "recommended_queries": recommended_queries
        }
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[ERROR] /recommend failed: {str(e)}\n{error_details}")
        raise HTTPException(status_code=500, detail=f"Error processing recommendation: {str(e)}\n{error_details}")


@api.post("/speech-to-text")
async def speech_to_text(file: UploadFile,language: str = Form("en")):
    try:
        temp_filename = f"temp_{file.filename}"
        with open(temp_filename, "wb") as temp_file:
            temp_file.write(await file.read())

        with open(temp_filename, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                file=(temp_filename, audio_file.read()),
                model="whisper-large-v3",
                response_format="verbose_json",
                language=language
            )

        os.remove(temp_filename)

        return {
            "transcription": getattr(transcription, "text", ""),
            "detected_language": getattr(transcription, "language", language)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing audio file: {str(e)}")

@api.post("/translate")
async def translate(text: str):
    try:
        translated_text = await translate_to_english(text)
        return {"original_text": text, "translated_text": translated_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error translating text: {str(e)}")
    
@api.post("/text-to-speech")
async def text_to_speech(text: str, voice: str = Form("Aaliyah-PlayAI")):
    try:
        unique_id = str(uuid.uuid4())
        output_dir = Path("speech_output")
        output_dir.mkdir(exist_ok=True) 
        
        speech_file_path = output_dir / f"{unique_id}.wav"
     
        response = client.audio.speech.create(
            model="playai-tts",  
            voice=voice,        
            response_format="wav", 
            input=text         
        )
        
   
        try:
            with open(speech_file_path, "wb") as f:
                response.write_to_file(speech_file_path)
        except AttributeError as e:
            raise AttributeError(f"Groq response object does not have expected method 'write_to_file'. Error: {e}")
        finally:
            if speech_file_path.exists():
                os.remove(speech_file_path)
        return FileResponse(
            path=speech_file_path,
            media_type="audio/wav",
            filename=f"speech_{unique_id}.wav" 
        )
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error generating speech: {str(e)}\n{error_details}") 
        raise HTTPException(status_code=500, detail=f"Error generating speech: {str(e)}")
    
    
@api.post("/search-completions")
async def search_completions(request: SearchCompletionsRequest):
    term, limit, config = request.term, request.limit, request.database_config
    completions, schema = [], None

    
    if config:
        try:
            _, engine = configure_db(
                config.dbtype, config.host, config.user, config.password, config.dbname
            )
            schema = get_database_schema(engine)
        except Exception as e:
            print(f"[Warning] Failed to load DB schema: {e}")

    
    if schema:
        prompt = (
            f"Given the following database schema:\n{schema}\n\n"
            f"Generate relevant search suggestions or autocompletions for a user.\n"
            f"The user has typed the partial term: \"{term}\"\n"
            f"Provide up to {limit} suggestions related to the schema.\n"
            f"Output as a JSON list of strings."
        )
    else:
        prompt = (
            f"Generate general database-related autocompletions.\n"
            f"The user has typed the partial term: \"{term}\"\n"
            f"Suggest up to {limit} completions with SQL keywords or query phrases.\n"
            f"Output as a JSON list of strings."
        )

    
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            temperature=0.2,
            max_tokens=256,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "You are an assistant providing database query autocompletions."},
                {"role": "user", "content": prompt}
            ]
        )

        content = response.choices[0].message.content
        completions = []
        if content:
            try:
                parsed = json.loads(content)
                completions = parsed.get("suggestions") if isinstance(parsed, dict) else parsed
            except json.JSONDecodeError:
                print(f"[Warning] Invalid JSON from LLM: {content}")
                completions = re.findall(r'"(.*?)"', content) if content else []
        else:
            completions = []
    except Exception as e:
        print(f"[Error] LLM failure for term '{term}': {e}\n{traceback.format_exc()}")
        completions = [f"Error generating suggestions for '{term}'"]
    if not isinstance(completions, list):
        completions = []
    return {"completions": completions[:limit]}



@api.post("/graphrecommender")
async def recommend_graph(request: GraphRecommendationRequest) -> Dict[str, List[str]]:
    data = request.sql_result_json

    
    if not data or not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
        raise HTTPException(status_code=400, detail="Invalid input: Expected a list of dictionaries.")

    
    try:
        data_preview = json.dumps(data[:5], indent=2)
        total_json_size = len(json.dumps(data))
        if total_json_size > 1500 and len(data_preview) > 1000:
            data_preview = data_preview[:1000] + "\n... (data truncated)"
        elif len(data) > 5:
            data_preview += "\n... (more rows exist)"
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process input data preview: {e}")

    
    column_names = list(data[0].keys()) if data else []
    
    # Analyze the data structure to make smart recommendations
    numeric_columns = []
    categorical_columns = []
    date_columns = []
    
    if data:
        sample = data[0]
        for col, value in sample.items():
            if isinstance(value, (int, float)) or (isinstance(value, str) and value.replace('.', '').replace('-', '').isdigit()):
                numeric_columns.append(col)
            elif isinstance(value, str):
                # Check if it might be a date
                if any(keyword in col.lower() for keyword in ['date', 'time', 'created', 'updated', 'year', 'month']):
                    date_columns.append(col)
                else:
                    categorical_columns.append(col)
    
    # Determine best chart types based on data structure
    recommended_charts = []
    
    # If we have numeric and categorical data
    if numeric_columns and categorical_columns:
        if len(data) <= 10:
            recommended_charts = ["pie", "bar", "line"]
        elif any(keyword in str(categorical_columns).lower() for keyword in ['time', 'date', 'year', 'month']):
            recommended_charts = ["line", "area", "bar"]
        else:
            recommended_charts = ["bar", "pie", "line"]
    
    # If we have multiple numeric columns
    elif len(numeric_columns) >= 2:
        recommended_charts = ["scatter", "bar", "line"]
    
    # If we only have numeric data
    elif numeric_columns:
        recommended_charts = ["bar", "line", "area"]
    
    # If we only have categorical data
    elif categorical_columns:
        recommended_charts = ["pie", "bar"]
    
    # Default fallback
    if not recommended_charts:
        recommended_charts = ["bar", "pie", "line"]

    # Use LLM as a secondary validation/refinement
    prompt = (
        f"Data structure analysis:\n"
        f"- Rows: {len(data)}\n"
        f"- Columns: {column_names}\n"
        f"- Numeric columns: {numeric_columns}\n"
        f"- Categorical columns: {categorical_columns}\n"
        f"- Date columns: {date_columns}\n\n"
        f"Current recommendation: {recommended_charts}\n\n"
        f"Based on this data structure, confirm or refine the chart recommendations.\n"
        f"Respond with exactly 3 chart types from: bar, line, pie, area, scatter, heatmap\n"
        f"Format: chart1, chart2, chart3"
    )

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant", 
            temperature=0.2, 
            max_tokens=50, 
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert data visualization assistant. Recommend the 3 best chart types for the given data structure."
                },
                {"role": "user", "content": prompt}
            ]
        )

        content = response.choices[0].message.content
        if content:
            content = content.strip()
            llm_charts = [chart.strip().lower() for chart in content.split(',')]
            valid_charts = ['bar', 'line', 'pie', 'area', 'scatter', 'heatmap']
            filtered_charts = [chart for chart in llm_charts if chart in valid_charts]
            if len(filtered_charts) >= 2:
                recommended_charts = filtered_charts[:3]

    except Exception as e:
        print(f"[Warning] LLM refinement failed: {e}")
        # Keep our original recommendation
        pass

    # Ensure we always have at least 2-3 recommendations
    if len(recommended_charts) < 2:
        recommended_charts.extend(["bar", "pie", "line"])
    
    # Remove duplicates while preserving order
    final_charts = []
    for chart in recommended_charts:
        if chart not in final_charts:
            final_charts.append(chart)
    
    return {"recommended_graphs": final_charts[:3]}

load_dotenv()

TWILIO_NUMBER = os.getenv("TWILLIO_NUMBER")  
ACCOUNT_SID    = os.getenv("ACCOUNT_SID")
AUTH_TOKEN    = os.getenv("AUTH_TOKEN")

# Check for missing Twilio configuration
if not all([TWILIO_NUMBER, ACCOUNT_SID, AUTH_TOKEN]):
    print("Warning: Twilio environment variables not set. WhatsApp bot functionality will be limited.")
    print("Please set TWILLIO_NUMBER, ACCOUNT_SID, and AUTH_TOKEN in your .env file")

CHAT_API_URL  = "http://localhost:1111/chat"   

@api.post("/whatsapp")
async def whatsapp_webhook(From: str = Form(...), Body: str = Form(...)):
    """
    Twilio will POST here on incoming WhatsApp messages.
    Expect Body to be a JSON string:
    {
      "database_config": { dbtype, host, user, password, dbname },
      "query_request":   { query }
    }
    """
    resp = MessagingResponse()

    try:
        payload = json.loads(Body.strip())
        assert "database_config" in payload and "query_request" in payload
    except Exception:
        resp.message(
            "⚠️ Please send a valid JSON with 'database_config' and 'query_request'.\n"
            "Example:\n"
            "{\n"
            '  "database_config": {"dbtype":"postgresql","host":"...","user":"...","password":"...","dbname":"..."},\n'
            '  "query_request": {"query":"count users"}\n'
            "}"
        )
        return Response(content=str(resp), media_type="application/xml")

    try:
        r = requests.post(CHAT_API_URL, json=payload, timeout=30)
        r.raise_for_status()
        result = r.json()
    except Exception as e:
        resp.message(f"❌ Error calling chat API:\n{e}")
        return Response(content=str(resp), media_type="application/xml")

    # format and send back
    sql      = result.get("sql_query", "<none>")
    summary  = result.get("summary", "<none>")
    title    = result.get("title", "")
    rows     = result.get("sql_result")
    # truncate very long results
    rows_str = json.dumps(rows, indent=2)
    if len(rows_str) > 800:
        rows_str = rows_str[:800] + "\n…(truncated)"

    msg = (
        f"✅ *Query OK*\n\n"
        f"*SQL:*```{sql}```\n\n"
        f"*Title:* {title}\n\n"
        f"*Summary:* {summary}\n\n"
        f"*Rows:*```json\n{rows_str}\n```"
    )
    resp.message(msg)

    return Response(content=str(resp), media_type="application/xml")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(api, port=1111)

