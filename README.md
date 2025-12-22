# Sales Assistant

AI-powered sales data query application with support for Gemini Flash and Ollama local models.

## Features

- Natural language queries to sales database
- AI chat interface with conversation history
- SQL query generation and execution
- Table visualization of results
- Debug mode to show generated SQL queries
- Conversation management (save, load, delete)
- **Configurable LLM provider**: Choose between Gemini (cloud) or Ollama (local)

## Setup

```bash
pip install -r requirements.txt
```


### Configure

Initialize the database:

```bash
python init_db.py
```

in `.env` file:

**Option A: Using Gemini (cloud)**
```
LLM_PROVIDER=gemini
GOOGLE_API_KEY=your_api_key_here
```

**Option B: Using Ollama (local)**
```
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

For Ollama, make sure you have Ollama installed and running locally. Install from https://ollama.ai and pull your desired model (e.g., `ollama pull llama3.2`).


### Run the application

```bash
python app.py
```

Open your browser and navigate to:

```
http://localhost:5000
```

For Ollama, make sure the model is available and the server is running, for example:

```bash
ollama list
ollama pull llama3.2  # also update
ollama run llama3.2
```


## Configuration

Edit `config.py` or `.env` to change settings:

**LLM Provider Settings:**
- `LLM_PROVIDER`: Choose 'gemini' or 'ollama' (default: 'gemini')
- `GEMINI_MODEL`: Gemini model to use (default: 'gemini-2.5-flash')
- `OLLAMA_BASE_URL`: Ollama server URL (default: 'http://localhost:11434')
- `OLLAMA_MODEL`: Ollama model name (default: 'llama3.2')

**Application Settings:**
- `DEBUG`: Enable/disable debug mode
- `SHOW_SQL_QUERIES`: Show/hide SQL queries in responses (always true in dev config, see DevelopmentConfig)
- `DB_PATH`: Path to SQLite database
- `MAX_ITERATIONS`: Maximum LLM iterations for tool calls (default: 5)


## Database Schema

- **customers**: Customer information
- **products**: Product catalog
- **orders**: Order records
- **order_items**: Order line items

## Example Queries

- "What are the top 5 customers by order value?"
- "Show me all products in the Electronics category"
- "What were the sales sum last month?"
- "Which products have low stock?"
- "Show me recent orders with status 'processing'"
