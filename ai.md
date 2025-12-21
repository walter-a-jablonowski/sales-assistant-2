
I want to make an app with sales data that a salesperson can use to query a database and ask questions about the data. We use Python for this project.

- For simplicity we use SQLite for now, we already have a sales.db that was made with init_db.py
- We use FastMCP for accessing the data: https://gofastmcp.com, https://github.com/jlowin/fastmcp
  - we already have mcp_server.py
- LLM: We use gemini flash for now. I provided the API key in .env
- We need to add:
  - Backend: use Flask
  - Frontend: javascript and html
  - UI: The user enters a query in natural language

Do you have any clarification questions?

 --

I agree.

Here are are the answers for the remaining clarification:

- Show the SQL query that was generated only in a debug mode that we can set in a confi. Use a config tht is typical for a flask app.
- Always show query and results
- Make an AI chat interface
- Show the conversatoin history and make past conversations accessible in a left sidebar
- Display errors in the UI e.g. as part of the chat, let the user continue entering follow ups if it was no critical error.
- config.py was from an old app, replace it with a typical flask config
