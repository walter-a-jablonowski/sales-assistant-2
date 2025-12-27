
See also

- AI Biz > Sell AI apps
- misc/dev_info


This app currently supports Gemini Flash or Ollama for LLM access. I#d like to add OpenRouter as a third option.


- [ ] Text output seems to be missing
  - maybe cause of problems with small models

- [ ] maybe tell the ai in the prompt that it may use markdown, so that it uses that every time
  - simple rendering added, maybe use te one from overview

- [ ] Modify when table/text/diagr appear ?
  - Tables are no sep tool because they're from execute_sql_query("SELECT * FROM customers LIMIT 5")
  - Diagr are a sep tool

- [ ] maybe make a second (cooler) UI design (keep current for dev demo)

### Models

- deepseek-r1:8b           smart for this machine but no tools
- nomic-embed-text:latest

maybe Del

- [x] Qwen2.5-coder        less good with current prompt
- [-] llama3.2             returns only some json with current prompt
- [-] glm4:latest          no support for tools
- [-] qwen2.5-coder:14b    ugly response with current prompt

Spec (can o diagrams ?)

- [ ] duckdb-nsql:7b

Capable local (less usful, models too big)
(if available: mistral:7b-q4_k, quantization shrink VRAM + RAM needs drastically with minimal quality loss)

- [-] deepseek-r1:8b  no support for tools
- [?] gpt-oss:20b     model requires more system memory (9.9 GiB) than is available (7.6 GiB)
- [?] mistral:7b      slow, less good results with current prompt
- [?] qwen3-coder     ChatGPT: 4 GB VRAM is far too small

Ollama cloud (limits)

- large models
  - https://ollama.com/library/gemini-3-flash-preview
  - deepseek-v3.1:671b-cloud
  - gpt-oss:120b-cloud
  - qwen3-coder:480b-cloud
  - Qwen3 (235B)
  - Llama 3.1 (405B)
- lmsys coder
  - glm-4.6:cloud           https://ollama.com/library/glm-4.6           these might be premium models (unavailable)
  -                         https://ollama.com/library/kimi-k2-thinking
  - kimi-k2:1t-cloud        https://ollama.com/library/kimi-k2
  -                         https://ollama.com/library/minimax-m2
  - qwen3-coder:480b-cloud  https://ollama.com/library/qwen3-coder 480b


### Make solid

- [ ] try stuff
- [ ] see minor code tasks

- [x] Verify if we already satisfy this requirement

  To ensure that the LLM writes valid SQL, ensure that:

  - force the LLM to choose only from a machine-provided schema contract
  - the schema is exposed as a tool
    - Create a tool that returns authoritative schema metadata
    - The LLM must call this tool first
  - Force SQL generation through a constrained function
  - Validate server-side before execution
    ```
    for each column in request:
      if column not in schema[table]:
        reject
    ```
    (Verified: `db_helpers.py` contains `validate_sql_against_schema` which checks tables and columns against the schema before execution)


Done
----------------------------------------------------------

### 2025-12-25

- [x] make edit-save-btn white
- [x] keep edit-message-btn always visible
- [x] upd the limited ai use msg if limits in ollama as well
  update the property SHOW_LIMITED_AI_WARNING: returns true if LLM_PROVIDER == 'gemini' or when OLLAMA_MODEL contains "cloud"

- [?] Unsure about that: Sometimes there seems to be an empty message when I re-run a message (maye when a message was send a second time)
  <div class="message assistant-message"><div class="message-content"></div></div>

- [x] add the currently used model to the placeholder of user-input

- [x] edit-message-btn doesn't work when clicked

- [x] ability to launch a question again
  ```
  Can we add the ability to launch a user question that was already processed by the ai again? Make it editable and when the user runs it again replace all following old conversation.
  ```
  - [x]
    - There is a horizontal line visible below "SQL Query" when it is folded, remove it 

    Restarting messages:

    - It would be better if we could edit the question in place instead of copying it to user-input
    - Also the AI output must replace the original AI output. This is just like how ChatGPT does it. Currently the new LLM outout is appended below. 

- [x] Make the sql-query-toggle look simpler: no bg color or border

- [x] Add a config setting DEMO_MODE. When this is set to true display a small below chat-input-container with the text "powered by © Walter A. Jablonowski 2025". Make sure it looks good with the design.

- [x] Currently the generated SQL query is shown in debug mode. Could we change that to always visible but inside a folded element? Make sure it looks good in the UI.

- [x] add a quick diagramming feature?
  ```
  Can we give the AI the ability to generate a result diagram if that this makes sense to present the result? Currently the AI presents results as table and text. The AI chooses the best type of diagram for this. I's duggest to use a popular diagramming library.
  ```

  - [x] Explain: Why is making a table no mcp tool while making a diagram is one?

- [x] get_db_connection, get_schema_dict, validate_sql_against_schema exists 2 times
- [x] you added generate_diagram as tool, explain why it is missing in mcp_server.py
- [x] max it prod was 5

### 2025-12-22

- maybe simulate

  - [x] verify: non critical errors are part of conversation and replaced when resolved (e.g. second try)
  - [x] verify: critical errors full error page

- [x] add a limited gemini uses in this demo msg (config arg)
  ```
  Add a message "Limited AI use" in the chat-header right aligned. Make it red. Show this message only when a new config entry is set to true. Set it true when the LLM is gemini.
  ```

- [x] responsive

- [x] upgrade so that we can also work with ollama
  ```
  I need to upgeade this app so tht beside the gemini flash model that we are currently using it also must be usable with ollama and a configurable local model. We use config.py to choose whether we want to use a local model or an online provider like gemini.
  ```

- [x]

  Currently I only see SQL an a table in the chat response. Make the LLM also say a few words as a summary for the result.

### 2025-12-21

- [x]

  When I set DEBUG = False the SQL query is still visible in the chat output. Show SQL only when debug is true.

- [x] make the bg color of the left sidebar a little darker (nicer)

- [x]

  Error handling updates:

  Resolvable errors:

  In conversations when there is an app error keep non critical errors as part as the conversation. Remove the error if it can be solved through further user action. Sample for a situation like this: the LLM responds that it has woo many requests, then the user enters a prompt a second time and it works.

  Currently conversations that have an error aren't persistent in the sidebar. Keep them there.

  Critical errors:

  If there is a critical app error so that the app can't work, replace the full html body with an error page (the app stops).

- [x] Whan I just write 'la'

  Error:
  'NoneType' object has no attribute 'name'

### Before

- [x]

  - google's current model seems to be: gemini-2.5-flash
  - max_iterations is set to 5, is it a good idea to reduce it to 2? Free daily usage of gemini flash models is used up pretty fast.
  - shortly list where in the code validations are happening and what is validated

- [x] move all constants and variables that ideally are in a config to a new config (e.g. max_iterations)
- [x] when something goes wrong e.g. model unavailable we need error messages in the UI, currently there is just an error in the console
