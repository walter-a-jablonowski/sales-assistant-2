# Sales Assistant

AI-powered sales data query application using Gemini Flash and Flask.

## Features

- Natural language queries to sales database
- AI chat interface with conversation history
- SQL query generation and execution
- Table visualization of results
- Debug mode to show generated SQL queries
- Conversation management (save, load, delete)

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Make sure `.env` file exists with your Google API key:
```
GOOGLE_API_KEY=your_api_key_here
```

3. Initialize the database:
```bash
python init_db.py
```

4. Run the application:
```bash
python app.py
```

5. Open your browser and navigate to:
```
http://localhost:5000
```

## Configuration

Edit `config.py` to change settings:

- `DEBUG`: Enable/disable debug mode
- `SHOW_SQL_QUERIES`: Show/hide SQL queries in responses
- `DB_PATH`: Path to SQLite database

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
