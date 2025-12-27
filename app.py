from flask import Flask, render_template, request, jsonify, session
from config import config
import db_helpers
import json
import uuid
from datetime import datetime
import os
from llm_provider import create_llm_provider
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)
app.config.from_object(config['development'])  # tASK: what about production?

if not os.path.exists('logs'):
  os.makedirs('logs')

file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240000, backupCount=10)
file_handler.setFormatter(logging.Formatter(
  '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
app.logger.info('Sales Assistant startup')

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
  },
  {
    'name': 'generate_diagram',
    'description': 'Generate a visual diagram/chart to present data insights. Use this when data is better understood visually (trends, comparisons, distributions). Choose the most appropriate chart type for the data.',
    'parameters': {
      'type': 'object',
      'properties': {
        'chart_type': {
          'type': 'string',
          'description': 'Type of chart to generate',
          'enum': ['bar', 'line', 'pie', 'doughnut', 'radar', 'polarArea']
        },
        'title': {
          'type': 'string',
          'description': 'Chart title'
        },
        'labels': {
          'type': 'array',
          'description': 'Labels for the data points (e.g., product names, months, categories)',
          'items': {'type': 'string'}
        },
        'datasets': {
          'type': 'array',
          'description': 'Array of datasets to plot. Each dataset contains label and data values.',
          'items': {
            'type': 'object',
            'properties': {
              'label': {'type': 'string', 'description': 'Dataset label'},
              'data': {'type': 'array', 'items': {'type': 'number'}, 'description': 'Numeric data values'}
            }
          }
        }
      },
      'required': ['chart_type', 'title', 'labels', 'datasets']
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
        'query': query,
        'columns': result['columns'],
        'rows': result['rows'],
        'row_count': result['row_count']
      }
    else:
      return {
        'type': 'error',
        'error': result['error'],
        'query': query
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
  
  elif function_name == 'generate_diagram':
    return {
      'type': 'diagram',
      'chart_type': function_args.get('chart_type', 'bar'),
      'title': function_args.get('title', ''),
      'labels': function_args.get('labels', []),
      'datasets': function_args.get('datasets', [])
    }
  
  return {'type': 'error', 'error': f'Unknown function: {function_name}'}

@app.route('/')
def index():
  if app.config['LLM_PROVIDER'] == 'gemini':
    model_name = app.config['GEMINI_MODEL']
  elif app.config['LLM_PROVIDER'] == 'openrouter':
    model_name = app.config['OPENROUTER_MODEL']
  else:
    model_name = app.config['OLLAMA_MODEL']
  
  return render_template('index.html', 
    show_limited_ai_warning=app.config['SHOW_LIMITED_AI_WARNING'],
    demo_mode=app.config['DEMO_MODE'],
    model_name=model_name)

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
            
            if hasattr(function_call, 'args'):
              function_args = function_call.args if isinstance(function_call.args, dict) else dict(function_call.args)
            else:
              function_args = {}
            
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
    app.logger.error(f'Error in chat endpoint: {str(e)}', exc_info=True)
    
    error_message = str(e)
    is_critical = True
    
    if 'rate' in error_message.lower() or 'quota' in error_message.lower() or 'limit' in error_message.lower():
      is_critical = False
      error_message = 'Rate limit reached. Please wait a moment and try again.'
      app.logger.warning(f'Rate limit hit for conversation {conversation_id}')
    elif 'timeout' in error_message.lower() or 'connection' in error_message.lower():
      is_critical = False
      error_message = 'Connection issue. Please try again.'
      app.logger.warning(f'Connection issue for conversation {conversation_id}')
    else:
      app.logger.error(f'Critical error for conversation {conversation_id}: {error_message}')
    
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
      except Exception as save_error:
        app.logger.error(f'Failed to save error to conversation: {str(save_error)}')
    
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
    app.logger.error(f'Error loading conversations: {str(e)}', exc_info=True)
    return jsonify({'error': str(e)}), 500

@app.route('/api/conversations/<conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
  try:
    conversations = load_conversations()
    conversation = conversations.get(conversation_id)
    
    if not conversation:
      app.logger.warning(f'Conversation not found: {conversation_id}')
      return jsonify({'error': 'Conversation missing'}), 404
    
    return jsonify(conversation)
  
  except Exception as e:
    app.logger.error(f'Error getting conversation {conversation_id}: {str(e)}', exc_info=True)
    return jsonify({'error': str(e)}), 500

@app.route('/api/conversations/<conversation_id>', methods=['DELETE'])
def delete_conversation(conversation_id):
  try:
    conversations = load_conversations()
    
    if conversation_id not in conversations:
      app.logger.warning(f'Attempted to delete non-existent conversation: {conversation_id}')
      return jsonify({'error': 'Conversation missing'}), 404
    
    del conversations[conversation_id]
    save_conversations(conversations)
    app.logger.info(f'Deleted conversation: {conversation_id}')
    
    return jsonify({'success': True})
  
  except Exception as e:
    app.logger.error(f'Error deleting conversation {conversation_id}: {str(e)}', exc_info=True)
    return jsonify({'error': str(e)}), 500

@app.route('/api/chat/rerun', methods=['POST'])
def rerun_message():
  try:
    data = request.json
    conversation_id = data.get('conversation_id')
    message_index = data.get('message_index')
    new_message = data.get('new_message', '').strip()
    
    if not conversation_id or message_index is None or not new_message:
      return jsonify({'error': 'Missing required parameters'}), 400
    
    conversations = load_conversations()
    
    if conversation_id not in conversations:
      return jsonify({'error': 'Conversation not found'}), 404
    
    conversation = conversations[conversation_id]
    
    if message_index >= len(conversation['messages']):
      return jsonify({'error': 'Invalid message index'}), 400
    
    conversation['messages'] = conversation['messages'][:message_index]
    
    conversation['messages'].append({
      'role': 'user',
      'content': new_message,
      'timestamp': datetime.now().isoformat()
    })
    
    save_conversations(conversations)
    
    chat_history = []
    for msg in conversation['messages']:
      if msg['role'] == 'user':
        chat_history.append({'role': 'user', 'parts': [{'text': msg['content']}]})
      elif msg['role'] == 'assistant':
        parts = []
        if msg.get('content'):
          parts.append({'text': msg['content']})
        if msg.get('function_results'):
          for func_result in msg['function_results']:
            parts.append({
              'function_call': {
                'name': func_result.get('name', ''),
                'args': func_result.get('args', {})
              }
            })
            parts.append({
              'function_response': {
                'name': func_result.get('name', ''),
                'response': func_result
              }
            })
        if parts:
          chat_history.append({'role': 'model', 'parts': parts})
    
    iteration = 0
    while iteration < app.config['MAX_ITERATIONS']:
      iteration += 1
      
      response = llm_client.generate_content(
        contents=chat_history,
        system_instruction=app.config['SYSTEM_PROMPT'],
        tools=[{'function_declarations': tools}]
      )
      
      assistant_text = ''
      current_function_calls = []
      
      for part in response.parts:
        if hasattr(part, 'function_call'):
          current_function_calls.append(part.function_call)
        elif hasattr(part, 'text'):
          assistant_text += part.text
      
      if current_function_calls:
        function_results = []
        
        for function_call in current_function_calls:
          function_name = function_call.name if hasattr(function_call, 'name') and function_call.name else None
          if not function_name:
            continue
          
          if hasattr(function_call, 'args'):
            function_args = function_call.args if isinstance(function_call.args, dict) else dict(function_call.args)
          else:
            function_args = {}
          
          result = execute_function_call(function_name, function_args)
          result['name'] = function_name
          result['args'] = function_args
          function_results.append(result)
        
        conversation['messages'].append({
          'role': 'assistant',
          'content': assistant_text,
          'function_results': function_results,
          'timestamp': datetime.now().isoformat()
        })
        
        save_conversations(conversations)
        
        chat_history.append({'role': 'model', 'parts': [{'text': assistant_text}] if assistant_text else []})
        
        for func_result in function_results:
          chat_history[-1]['parts'].append({
            'function_call': {
              'name': func_result['name'],
              'args': func_result['args']
            }
          })
          chat_history.append({
            'role': 'function',
            'parts': [{
              'function_response': {
                'name': func_result['name'],
                'response': func_result
              }
            }]
          })
        
        if assistant_text:
          break
      else:
        conversation['messages'].append({
          'role': 'assistant',
          'content': assistant_text,
          'timestamp': datetime.now().isoformat()
        })
        
        save_conversations(conversations)
        break
    
    return jsonify({'success': True, 'conversation_id': conversation_id})
  
  except Exception as e:
    app.logger.error(f'Error in rerun endpoint: {str(e)}', exc_info=True)
    return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
  app.run(debug=app.config['DEBUG'], port=5000)
