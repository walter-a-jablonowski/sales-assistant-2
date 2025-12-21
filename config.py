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

When answering questions:
1. First, use get_database_schema() to understand the database structure if needed
2. Use get_sample_data() to see example data if helpful
3. Generate and execute SQL queries using execute_sql_query()
4. Provide clear, concise answers based on the data
5. If you encounter errors, explain them clearly and suggest alternatives

Always be helpful and accurate.'''

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
