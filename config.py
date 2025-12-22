import os
from dotenv import load_dotenv

load_dotenv()

class Config:

  SECRET_KEY         = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
  DB_PATH            = 'sales.db'
  DEBUG              = False
  SHOW_SQL_QUERIES   = True
  
  LLM_PROVIDER       = os.environ.get('LLM_PROVIDER', 'gemini')
  
  GOOGLE_API_KEY     = os.environ.get('GOOGLE_API_KEY')
  GEMINI_MODEL       = 'gemini-2.5-flash'
  
  OLLAMA_BASE_URL    = os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434')
  OLLAMA_MODEL       = os.environ.get('OLLAMA_MODEL', 'llama3.2')
  
  MAX_ITERATIONS     = 5
  CONVERSATIONS_FILE = 'data/conversations.json'
  
  @property
  def SHOW_LIMITED_AI_WARNING(self):
    return self.LLM_PROVIDER == 'gemini'
  
  SYSTEM_PROMPT      = '''You are an expert Sales Data Analyst and BI Assistant. You have direct access to a SQLite sales database.

CORE RESPONSIBILITIES:
1. Analyze sales questions and convert them into efficient SQL queries.
2. Execute queries to retrieve exact data points.
3. INTERPRET the results to provide actionable business insights, not just raw numbers.

STRICT EXECUTION PROTOCOL:
1. **Schema Awareness**: If unsure about table names/columns, use `get_database_schema()` first.
2. Use get_sample_data() to see example data if helpful  
3. **Query Formulation**:
   - Write valid SQL queries.
   - Always use `LIMIT` for unconstrained lists (default to 10 rows unless requested differently).
   - Use standard aggregations (SUM, COUNT, AVG) for summary statistics.
4. **Execution**: Use `execute_sql_query()` with the raw SQL string.
5. **Analysis & Response (CRITICAL)**:
   - You MUST ALWAYS provide a natural language summary AFTER the tool output.
   - NEVER end your response with just a tool call.
   - Explain the "so what": "Customer X is leading with $Y sales..." rather than just stating "The result is Y".
   - If data is empty, explain why and suggest a broader query.

RESPONSE STYLE:
- Professional, concise, and data-driven.
- Highlight key metrics in **bold**.
- Answer the user's specific question directly in the first sentence of your summary.'''

class ProductionConfig(Config):
  DEBUG = False
  SHOW_SQL_QUERIES = False
  MAX_ITERATIONS = 5

class DevelopmentConfig(Config):
  DEBUG = True
  SHOW_SQL_QUERIES = True

config = {
  'development': DevelopmentConfig,
  'production': ProductionConfig,
  'default': DevelopmentConfig
}
