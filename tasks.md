
See also

- AI Biz > Sell AI apps
- misc/dev_info


- [ ] ability to launch a question again
- [ ] Modify when table/text/diagr appear ?
  - Tables are no sep tool because they're from execute_sql_query("SELECT * FROM customers LIMIT 5")
  - Diagr are a sep tool

- [ ]

  - duckdb-nsql:7b

  - [-] llama3.2       returns only some json with current prompt
  
  - [x] Qwen2.5-coder  less good with current prompt
  - [-] gemma3:12b     
  - [-] gemma3         no support for tools
  - [ ] mistral:7b     

  Capable local

  - [ ] Llama 4 (Scout/Maverick)          67  -   245 GB
  - [ ] GPT-OSS (120B)                    14  - >  65 GB
  - [ ] DeepSeek-R1 (70B)         43 GB   5.2 -   404 GB
  - [ ] Qwen3-coder

  Ollama has cloud models you can run via Ollama CLI without local GPU limits:
  https://ollama.com/blog/cloud-models?utm_source=chatgpt.com

  - large models
    - https://ollama.com/library/gemini-3-flash-preview
    - deepseek-v3.1:671b-cloud
    - gpt-oss:120b-cloud
    - qwen3-coder:480b-cloud
    - Qwen3 (235B)
    - Llama 3.1 (405B)
  - lmsys coder
    - https://ollama.com/library/glm-4.6
    - https://ollama.com/library/kimi-k2-thinking
    - https://ollama.com/library/kimi-k2
    - https://ollama.com/library/minimax-m2
    - https://ollama.com/library/qwen3-coder 480b

- [ ] maybe tell the ai in the prompt that it may use markdown, so that it uses that every time
  - simple rendering added, maybe use te one from overview

- [ ] make sql foldable a little nicer
- [ ] maybe make a second (cooler) UI design (keep current for dev demo)


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
