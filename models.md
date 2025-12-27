
- gemini

Spec (can o diagrams ?)

- [ ] duckdb-nsql:7b


Ollama Current
----------------------------------------------------------

- deepseek-r1:8b           smart for this machine but no tools
- nomic-embed-text:latest

maybe Del

- [x] Qwen2.5-coder        less good with current prompt
- [-] llama3.2             returns only some json with current prompt
- [-] glm4:latest          no support for tools
- [-] qwen2.5-coder:14b    ugly response with current prompt


OpenRouter
----------------------------------------------------------

- Gemini 2.5 Flash / Flash-Lite
- Grok-3-mini-beta
- gpt-oss
- DeepSeek R1/V3
- Qwen, glm, kimi
- Claude Haiku, GPT-5 Mini


Ollama cloud (limits)
----------------------------------------------------------

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


Capable local (less usful, models too big)
----------------------------------------------------------

(if available: mistral:7b-q4_k, quantization shrink VRAM + RAM needs drastically with minimal quality loss)

- [-] deepseek-r1:8b  no support for tools
- [?] gpt-oss:20b     model requires more system memory (9.9 GiB) than is available (7.6 GiB)
- [?] mistral:7b      slow, less good results with current prompt
- [?] qwen3-coder     ChatGPT: 4 GB VRAM is far too small
