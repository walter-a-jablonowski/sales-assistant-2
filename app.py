from flask import Flask, render_template, request, jsonify, session
from config import config
import db_helpers
import json
import uuid
from datetime import datetime
import os
from llm_provider import create_llm_provider

app = Flask(__name__)
app.config.from_object(config['development'])  # tASK: what about production?

llm_client = create_llm_provider(app.config['LLM_PROVIDER'], config['development'])

tools = [
  {
    'name': 'get_database_schema',
    'description': 'Get the complete database schema including all tables and their columns. Use this to understand the database structure before writing queries.',
    'parameters': {
      'type': 'object',
      'properties': {},
      'required': []
    }
  },
  {
    'name': 'execute_sql_query',
    'description': 'Execute a read-only SQL SELECT query against the sales database. Returns the results as structured data.',
    'parameters': {
      'type': 'object',
      'properties': {
        'query': {
          'type': 'string',
          'description': 'A SELECT SQL query to execute (INSERT, UPDATE, DELETE are not allowed)'
        }
      },
      'required': ['query']
    }
  },
  {
    'name': 'get_sample_data',
    'description': 'Get sample rows from a specific table to understand the data structure.',
    'parameters': {
      'type': 'object',
      'properties': {
        'table_name': {
          'type': 'string',
          'description': 'Name of the table to sample',
          'enum': ['customers', 'products', 'orders', 'order_items']
        },
        'limit': {
          'type': 'integer',
          'description': 'Number of sample rows to return (default: 5)'
        }
      },
      'required': ['table_name']
    }
  }
]

CONVERSATIONS_FILE = app.config['CONVERSATIONS_FILE']

def load_conversations():
  if not os.path.exists('data'):
    os.makedirs('data')
  
  if os.path.exists(CONVERSATIONS_FILE):
    try:
      with open(CONVERSATIONS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)
    except:
      return {}
  return {}

def save_conversations(conversations):
  if not os.path.exists('data'):
    os.makedirs('data')
  
  with open(CONVERSATIONS_FILE, 'w', encoding='utf-8') as f:
    json.dump(conversations, f, indent=2, ensure_ascii=False)

def execute_function_call(function_name, function_args):
  if function_name == 'get_database_schema':
    result = db_helpers.get_database_schema()
    return {'type': 'text', 'content': result}
  
  elif function_name == 'execute_sql_query':
    query = function_args.get('query', '')
    result = db_helpers.execute_sql_query(query)
    
    if result['success']:
      return {
        'type': 'table',
        'query': query if app.config['SHOW_SQL_QUERIES'] else None,
        'columns': result['columns'],
        'rows': result['rows'],
        'row_count': result['row_count']
      }
    else:
      return {
        'type': 'error',
        'error': result['error'],
        'query': query if app.config['SHOW_SQL_QUERIES'] else None
      }
  
  elif function_name == 'get_sample_data':
    table_name = function_args.get('table_name', '')
    limit = function_args.get('limit', 5)
    result = db_helpers.get_sample_data(table_name, limit)
    
    if result['success']:
      return {
        'type': 'table',
        'table_name': table_name,
        'columns': result['columns'],
        'rows': result['rows'],
        'row_count': result['row_count']
      }
    else:
      return {
        'type': 'error',
        'error': result['error']
      }
  
  return {'type': 'error', 'error': f'Unknown function: {function_name}'}

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
  conversation_id = None
  conversations = None
  
  try:
    data = request.json
    user_message = data.get('message', '')
    conversation_id = data.get('conversation_id')
    
    if not user_message:
      return jsonify({'error': 'Message is required', 'is_critical': False}), 400
    
    conversations = load_conversations()
    
    if not conversation_id:
      conversation_id = str(uuid.uuid4())
      conversations[conversation_id] = {
        'id': conversation_id,
        'title': user_message[:50] + ('...' if len(user_message) > 50 else ''),
        'created_at': datetime.now().isoformat(),
        'messages': []
      }
    
    conversation = conversations.get(conversation_id)
    if not conversation:
      return jsonify({'error': 'Conversation missing', 'is_critical': False}), 404
    
    conversation['messages'].append({
      'role': 'user',
      'content': user_message,
      'timestamp': datetime.now().isoformat()
    })
    
    chat_history = []
    for msg in conversation['messages'][:-1]:
      if msg['role'] == 'user':
        chat_history.append({'role': 'user', 'parts': [{'text': msg['content']}]})
      elif msg['role'] == 'assistant':
        chat_history.append({'role': 'model', 'parts': [{'text': msg['content']}]})
    
    chat_history.append({'role': 'user', 'parts': [{'text': user_message}]})
    
    response = llm_client.generate_content(
      contents=chat_history,
      system_instruction=app.config['SYSTEM_PROMPT'],
      tools=[{'function_declarations': tools}]
    )
    
    function_results = []
    assistant_text = ''
    
    iteration = 0
    
    while iteration < app.config['MAX_ITERATIONS']:
      iteration += 1
      
      current_function_calls = []
      
      if response.candidates[0].content.parts:
        for part in response.candidates[0].content.parts:
          if hasattr(part, 'function_call') and part.function_call:
            current_function_calls.append(part.function_call)
          elif hasattr(part, 'text'):
            assistant_text += part.text
            
      if current_function_calls:
        for function_call in current_function_calls:
            function_name = function_call.name if hasattr(function_call, 'name') and function_call.name else None
            if not function_name:
              continue
            function_args = dict(function_call.args) if hasattr(function_call, 'args') else {}
            
            result = execute_function_call(function_name, function_args)
            function_results.append(result)
            
            chat_history.append({'role': 'model', 'parts': [{'function_call': function_call}]})
            chat_history.append({
              'role': 'user',
              'parts': [{
                'function_response': {
                  'name': function_name,
                  'response': result
                }
              }]
            })
            
        response = llm_client.generate_content(
          contents=chat_history,
          system_instruction=app.config['SYSTEM_PROMPT'],
          tools=[{'function_declarations': tools}]
        )
      else:
        break
    
    conversation['messages'].append({
      'role': 'assistant',
      'content': assistant_text,
      'function_results': function_results,
      'timestamp': datetime.now().isoformat()
    })
    
    save_conversations(conversations)
    
    return jsonify({
      'conversation_id': conversation_id,
      'message': assistant_text,
      'function_results': function_results
    })
  
  except Exception as e:
    error_message = str(e)
    is_critical = True
    
    if 'rate' in error_message.lower() or 'quota' in error_message.lower() or 'limit' in error_message.lower():
      is_critical = False
      error_message = 'Rate limit reached. Please wait a moment and try again.'
    elif 'timeout' in error_message.lower() or 'connection' in error_message.lower():
      is_critical = False
      error_message = 'Connection issue. Please try again.'
    
    if conversation_id and conversations:
      try:
        conversation = conversations.get(conversation_id)
        if conversation:
          conversation['messages'].append({
            'role': 'error',
            'content': error_message,
            'is_critical': is_critical,
            'timestamp': datetime.now().isoformat()
          })
          save_conversations(conversations)
      except:
        pass
    
    return jsonify({
      'error': error_message,
      'is_critical': is_critical,
      'conversation_id': conversation_id
    }), 500

@app.route('/api/conversations', methods=['GET'])
def get_conversations():
  try:
    conversations = load_conversations()
    
    conversation_list = []
    for conv_id, conv in conversations.items():
      conversation_list.append({
        'id': conv['id'],
        'title': conv['title'],
        'created_at': conv['created_at'],
        'message_count': len(conv['messages'])
      })
    
    conversation_list.sort(key=lambda x: x['created_at'], reverse=True)
    
    return jsonify({'conversations': conversation_list})
  
  except Exception as e:
    return jsonify({'error': str(e)}), 500

@app.route('/api/conversations/<conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
  try:
    conversations = load_conversations()
    conversation = conversations.get(conversation_id)
    
    if not conversation:
      return jsonify({'error': 'Conversation missing'}), 404
    
    return jsonify(conversation)
  
  except Exception as e:
    return jsonify({'error': str(e)}), 500

@app.route('/api/conversations/<conversation_id>', methods=['DELETE'])
def delete_conversation(conversation_id):
  try:
    conversations = load_conversations()
    
    if conversation_id not in conversations:
      return jsonify({'error': 'Conversation missing'}), 404
    
    del conversations[conversation_id]
    save_conversations(conversations)
    
    return jsonify({'success': True})
  
  except Exception as e:
    return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
  app.run(debug=app.config['DEBUG'], port=5000)
