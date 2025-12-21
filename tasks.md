
- [ ] bg color of left sidebar a little nicer (darker)

- [ ]
  In conversations when there is an app error keep non critical errors as part as the conversation until they are solved

where an error appears are missing in the sidebar

- [ ] Whan I just write 'la'

  Error:
  'NoneType' object has no attribute 'name'

- [ ] Verify if we already satisfy this requirement:

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

Done
----------------------------------------------------------

- [x]

  - google's current model seems to be: gemini-2.5-flash
  - max_iterations is set to 5, is it a good idea to reduce it to 2? Free daily usage of gemini flash models is used up pretty fast.
  - shortly list where in the code validations are happening and what is validated

- [x] move all constants and variables that ideally are in a config to a new config (e.g. max_iterations)
- [x] when something goes wrong e.g. model unavailable we need error messages in the UI, currently there is just an error in the console
