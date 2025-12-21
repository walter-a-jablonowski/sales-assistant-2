import os
from dotenv import load_dotenv

load_dotenv()

class Config:
  SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
  DB_PATH = 'sales.db'
  DEBUG = False
  SHOW_SQL_QUERIES = True
  GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
  
  GEMINI_MODEL = 'gemini-2.5-flash'
  MAX_ITERATIONS = 2
  CONVERSATIONS_FILE = 'data/conversations.json'
  
  SYSTEM_PROMPT = '''You are a helpful sales data assistant. You have access to a sales database with information about customers, products, orders, and order items.

CRITICAL INSTRUCTION: You MUST ALWAYS provide a text response after using tools. Never end your response with just a function call. After executing queries, you MUST write a summary in natural language.

When answering questions:
1. Use get_database_schema() to understand the database structure if needed
2. Use get_sample_data() to see example data if helpful  
3. Execute SQL queries using execute_sql_query()
4. After the query results are shown, ALWAYS write a text explanation summarizing:
   - What the data shows
   - Key insights or notable findings
   - Answer to the user's question in plain language

Example response pattern:
[Tool executes and shows table]
"Based on the data above, I can see that... The top customer is... This shows that..."

NEVER just call a function and stop. ALWAYS follow up with explanatory text.'''

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
