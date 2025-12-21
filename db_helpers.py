import sqlite3
import re
from config import Config

def get_db_connection():
  conn = sqlite3.connect(Config.DB_PATH)
  conn.row_factory = sqlite3.Row
  return conn

def get_schema_dict():
  conn = get_db_connection()
  cursor = conn.cursor()
  
  cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
  tables = cursor.fetchall()
  
  schema = {}
  for table in tables:
    table_name = table[0]
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    schema[table_name] = [col[1].lower() for col in columns]
  
  conn.close()
  return schema

def validate_sql_against_schema(query: str) -> tuple[bool, str]:
  schema = get_schema_dict()
  query_lower = query.lower()
  
  from_match = re.search(r'\bfrom\s+([\w,\s]+?)(?:\s+where|\s+group|\s+order|\s+limit|\s+join|$)', query_lower, re.IGNORECASE)
  if not from_match:
    return False, "Error: Couldn't parse FROM clause in query"
  
  tables_str = from_match.group(1).strip()
  tables = [t.strip().split()[0] for t in re.split(r',|\s+join\s+', tables_str) if t.strip()]
  
  for table in tables:
    if table not in schema:
      return False, f"Error: Table '{table}' doesn't exist in schema. Available tables: {', '.join(schema.keys())}"
  
  select_match = re.search(r'select\s+(.*?)\s+from', query_lower, re.IGNORECASE | re.DOTALL)
  if not select_match:
    return False, "Error: Couldn't parse SELECT clause"
  
  select_clause = select_match.group(1).strip()
  
  if select_clause == '*' or '*' in select_clause:
    return True, ""
  
  column_parts = [c.strip() for c in select_clause.split(',')]
  
  for col_expr in column_parts:
    col_expr_clean = re.sub(r'\s+as\s+\w+$', '', col_expr, flags=re.IGNORECASE).strip()
    
    if any(func in col_expr_clean.lower() for func in ['count(', 'sum(', 'avg(', 'max(', 'min(', 'group_concat(']):
      continue
    
    if '.' in col_expr_clean:
      parts = col_expr_clean.split('.')
      table_alias = parts[0].strip()
      col_name = parts[1].strip()
      
      found = False
      for table in tables:
        if col_name in schema.get(table, []):
          found = True
          break
      
      if not found:
        return False, f"Error: Column '{col_name}' missing in any queried table. Check schema."
    else:
      col_name = col_expr_clean.strip()
      
      found = False
      for table in tables:
        if col_name in schema.get(table, []):
          found = True
          break
      
      if not found and col_name not in ['*']:
        return False, f"Error: Column '{col_name}' missing in queried tables. Available columns: {', '.join([c for t in tables for c in schema.get(t, [])])}"
  
  return True, ""

def get_database_schema() -> str:
  conn = get_db_connection()
  cursor = conn.cursor()
  
  cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
  tables = cursor.fetchall()
  
  schema_info = []
  for table in tables:
    table_name = table[0]
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    
    schema_info.append(f"\nTable: {table_name}")
    schema_info.append("Columns:")
    for col in columns:
      col_name = col[1]
      col_type = col[2]
      is_pk = " (PRIMARY KEY)" if col[5] else ""
      not_null = " NOT NULL" if col[3] else ""
      schema_info.append(f"  - {col_name}: {col_type}{is_pk}{not_null}")
  
  conn.close()
  return "\n".join(schema_info)

def execute_sql_query(query: str) -> dict:
  query_upper = query.strip().upper()
  if not query_upper.startswith('SELECT'):
    return {
      'success': False,
      'error': "Only SELECT queries are allowed."
    }
  
  if any(keyword in query_upper for keyword in ['DROP', 'ALTER', 'CREATE', 'TRUNCATE']):
    return {
      'success': False,
      'error': "DDL statements (DROP, ALTER, CREATE, TRUNCATE) aren't allowed."
    }
  
  is_valid, error_msg = validate_sql_against_schema(query)
  if not is_valid:
    return {
      'success': False,
      'error': error_msg
    }
  
  try:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query)
    
    results = cursor.fetchall()
    columns = [description[0] for description in cursor.description]
    
    rows = []
    for row in results:
      rows.append([str(value) if value is not None else "NULL" for value in row])
    
    conn.close()
    
    return {
      'success': True,
      'columns': columns,
      'rows': rows,
      'row_count': len(rows)
    }
    
  except sqlite3.Error as e:
    return {
      'success': False,
      'error': f"SQL Error: {str(e)}"
    }
  except Exception as e:
    return {
      'success': False,
      'error': f"Error: {str(e)}"
    }

def get_sample_data(table_name: str, limit: int = 5) -> dict:
  allowed_tables = ['customers', 'products', 'orders', 'order_items']
  if table_name not in allowed_tables:
    return {
      'success': False,
      'error': f"Table must be one of {allowed_tables}"
    }
  
  try:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name} LIMIT ?", (limit,))
    
    results = cursor.fetchall()
    columns = [description[0] for description in cursor.description]
    
    rows = []
    for row in results:
      rows.append([str(value) if value is not None else "NULL" for value in row])
    
    conn.close()
    
    return {
      'success': True,
      'columns': columns,
      'rows': rows,
      'row_count': len(rows)
    }
    
  except sqlite3.Error as e:
    return {
      'success': False,
      'error': f"SQL Error: {str(e)}"
    }
  except Exception as e:
    return {
      'success': False,
      'error': f"Error: {str(e)}"
    }
