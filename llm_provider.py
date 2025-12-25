import google.genai as genai
import requests
import json
from typing import Dict, List, Any, Optional


class LLMProvider:
  
  def generate_content(self, contents: List[Dict], system_instruction: str, tools: List[Dict]) -> Any:
    raise NotImplementedError


class GeminiProvider(LLMProvider):
  
  def __init__(self, api_key: str, model: str):
    self.client = genai.Client(api_key=api_key)
    self.model = model
  
  def generate_content(self, contents: List[Dict], system_instruction: str, tools: List[Dict]) -> Any:
    return self.client.models.generate_content(
      model=self.model,
      contents=contents,
      config={
        'system_instruction': system_instruction,
        'tools': tools
      }
    )


class OllamaProvider(LLMProvider):
  
  def __init__(self, base_url: str, model: str):
    self.base_url = base_url.rstrip('/')
    self.model = model
  
  def generate_content(self, contents: List[Dict], system_instruction: str, tools: List[Dict]) -> Any:
    messages = self._convert_to_ollama_format(contents, system_instruction)
    ollama_tools = self._convert_tools_to_ollama_format(tools)
    
    payload = {
      'model': self.model,
      'messages': messages,
      'stream': False
    }
    
    if ollama_tools:
      payload['tools'] = ollama_tools
    
    response = requests.post(
      f"{self.base_url}/api/chat",
      json=payload,
      timeout=120
    )
    
    if response.status_code != 200:
      raise Exception(f"Ollama API error: {response.status_code} - {response.text}")
    
    return self._convert_ollama_response(response.json())
  
  def _convert_to_ollama_format(self, contents: List[Dict], system_instruction: str) -> List[Dict]:
    messages = []
    
    if system_instruction:
      messages.append({
        'role': 'system',
        'content': system_instruction
      })
    
    for content in contents:
      role = content.get('role', '')
      
      if role == 'model':
        role = 'assistant'
      
      parts = content.get('parts', [])
      
      for part in parts:
        if isinstance(part, dict):
          if 'text' in part:
            messages.append({
              'role': role,
              'content': part['text']
            })
          elif 'function_call' in part:
            func_call = part['function_call']
            
            if hasattr(func_call, 'name'):
              func_name = func_call.name
              func_args = func_call.args if isinstance(func_call.args, dict) else dict(func_call.args)
            else:
              func_name = func_call.get('name', '')
              func_args = func_call.get('args', {})
            
            messages.append({
              'role': role,
              'content': '',
              'tool_calls': [{
                'function': {
                  'name': func_name,
                  'arguments': func_args
                }
              }]
            })
          elif 'function_response' in part:
            func_resp = part['function_response']
            messages.append({
              'role': 'tool',
              'content': json.dumps(func_resp.get('response', {}))
            })
    
    return messages
  
  def _convert_tools_to_ollama_format(self, tools: List[Dict]) -> List[Dict]:
    if not tools:
      return []
    
    ollama_tools = []
    
    for tool_group in tools:
      if 'function_declarations' in tool_group:
        for func_decl in tool_group['function_declarations']:
          ollama_tools.append({
            'type': 'function',
            'function': {
              'name': func_decl.get('name', ''),
              'description': func_decl.get('description', ''),
              'parameters': func_decl.get('parameters', {})
            }
          })
    
    return ollama_tools
  
  def _convert_ollama_response(self, ollama_response: Dict) -> 'OllamaResponse':
    return OllamaResponse(ollama_response)


class OllamaResponse:
  
  def __init__(self, response_data: Dict):
    self.response_data = response_data
    self.candidates = [OllamaCandidate(response_data)]


class OllamaCandidate:
  
  def __init__(self, response_data: Dict):
    self.content = OllamaContent(response_data)


class OllamaContent:
  
  def __init__(self, response_data: Dict):
    self.parts = []
    
    message = response_data.get('message', {})
    content = message.get('content', '')
    tool_calls = message.get('tool_calls', [])
    
    if content:
      self.parts.append(OllamaTextPart(content))
    
    if tool_calls:
      for tool_call in tool_calls:
        self.parts.append(OllamaFunctionCallPart(tool_call))


class OllamaTextPart:
  
  def __init__(self, text: str):
    self.text = text


class OllamaFunctionCallPart:
  
  def __init__(self, tool_call: Dict):
    self.function_call = OllamaFunctionCall(tool_call)


class OllamaFunctionCall:
  
  def __init__(self, tool_call: Dict):
    func = tool_call.get('function', {})
    self.name = func.get('name', '')
    
    args_str = func.get('arguments', '{}')
    try:
      args_dict = json.loads(args_str) if isinstance(args_str, str) else args_str
    except:
      args_dict = {}
    
    self.args = args_dict


def create_llm_provider(provider_type: str, config: Any) -> LLMProvider:
  if provider_type == 'gemini':
    return GeminiProvider(
      api_key=config.GOOGLE_API_KEY,
      model=config.GEMINI_MODEL
    )
  elif provider_type == 'ollama':
    return OllamaProvider(
      base_url=config.OLLAMA_BASE_URL,
      model=config.OLLAMA_MODEL
    )
  else:
    raise ValueError(f"Unknown LLM provider: {provider_type}")
