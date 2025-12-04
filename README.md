# SugarGPT 

SugarGPT is a custom SugarCRM sidebar action (`sugargpt`) that opens a floating, draggable AI assistant directly inside the Sugar application.  
The popup embeds an iframe pointing to a local Python RAG app, allowing users to ask natural-language questions about SugarCRM using indexed documentation and an Ollama-hosted LLM.

This project demonstrates a modern, AI-powered extension to a legacy CRM platform—built cleanly, modularly, and without modifying core SugarCRM files.

---

## Features

- **Sidebar Action Button** — Adds a clean, inline icon to the SugarCRM sidebar for quick access.  
- **Floating Popup Window** — Draggable and resizable modal panel built with Sidecar + jQuery UI.  
- **Embedded AI Assistant** — Loads an iframe (`http://localhost:8080`) pointing to your Python RAG app.  
- **Full RAG Pipeline** — Uses Ollama embeddings + LLM completions with ChromaDB for retrieval.  
- **Dynamic CSS Injection** — Popup-specific styling injected via `.hbs` template without touching `custom.less`.  
- **Clean Lifecycle Management** — Popup initializes on demand and cleans up automatically when disposed.

---

## Demo

Here’s SugarGPT in action inside SugarCRM:

![SugarGPT Demo](demo/sugargpt_demo.gif)

The popup loads the RAG assistant UI, allowing real-time Q&A with context pulled from your indexed SugarCRM PDF documentation.

---

## File Structure

```
custom/
├─ clients/base/views/sugargpt/
│  ├─ sugargpt.hbs               # Sidebar nav item
│  ├─ sugargpt.js                # Popup logic, drag/resize, CSS injection
│  ├─ sugargpt.php               # Viewdefs + iframe source
│  ├─ sugargpt_popup.hbs         # Popup markup (iframe wrapper)
│  └─ sugargpt_popup_css.hbs     # Popup-specific styles
└─ Extension/application/Ext/clients/base/layouts/sidebar-nav/
   └─ add_sugargpt_action.php    # Registers SugarGPT in the sidebar navigation
```

---

## Installation

1. Copy these files into your SugarCRM instance, **merging into existing folders**.  
2. Run **Admin → Repair → Quick Repair and Rebuild**.  
3. Refresh SugarCRM.  
4. Click the new **SugarGPT icon** in the sidebar to open the AI assistant popup.  

To change the iframe source, update:

```php
$viewdefs["base"]["view"]["sugargpt"] = [
    'iframeSrc' => 'http://localhost:8080',
];
```

---

# Python RAG Backend (Embedded via iframe)

SugarGPT’s intelligence comes from a lightweight Python application that performs **retrieval-augmented generation** using SugarCRM documentation.

The backend uses:

- **ChromaDB** for vector storage  
- **nomic-embed-text** for embeddings (via Ollama)  
- **GPT-OSS:20B** or any other local LLM for generation  
- **Gradio** for the frontend UI  
- **OpenAI-compatible API** via Ollama  

This app runs at `http://localhost:8080`, which the popup loads inside SugarCRM.

---

## How It Works (Architecture)

```
[ Sidebar Icon ]
       ↓
[SugarGPT Popup]
       ↓ (iframe)
http://localhost:8080
       ↓
[ Gradio UI ] ←→ [ RAG Backend ]
       ↓
[ ChromaDB Vector Store ]
       ↓
[ Ollama Embeddings + LLM ]
```

All data stays local.  
All processing is fast.  
No external network calls.

---

## Backend Components

### **1. Gradio Frontend (`app.py`)**
Provides the UI loaded in the iframe:

- User input  
- AI output  
- Clear + Flag buttons  

---

### **2. PDF Indexing (`index_docs.py`)**
Processes all SugarCRM PDF documentation:

- Loads PDFs from `./docs/`  
- Splits text into overlapping chunks  
- Embeds each chunk using Ollama  
- Stores vectors + metadata in a Chroma collection  

Run indexing:

```bash
python index_docs.py
```

---

### **3. RAG Pipeline (`rag_backend.py`)**
When the user asks a question:

1. Embed the query  
2. Retrieve the most relevant documentation  
3. Build a context-aware prompt  
4. Query the LLM via Ollama  
5. Return the final answer  

---

## Running the RAG App

1. Add SugarCRM PDFs to the `docs/` directory  
2. Build the vector DB:  
   ```bash
   python index_docs.py
   ```
3. Start the AI server:  
   ```bash
   python app.py
   ```
4. Open SugarCRM → click the SugarGPT icon → start asking questions.

---

## Learning Purpose

This project demonstrates:

- Extending SugarCRM using Sidecar views, viewdefs, and HBS templates  
- Integrating modern AI tools into a legacy enterprise CRM  
- Building a full **retrieval-augmented generation (RAG)** system  
- Combining ChromaDB + Ollama for fast, local AI inference  
- Embedding external apps via iframe for clean customization  
- Applying maintainable architecture across frontend + backend  

It’s a practical example of AI-augmented CRM engineering.

---

## License

This customization is shared for educational and portfolio purposes.  
**Portions of this code are based on SugarCRM examples and are used under the Apache 2.0 license.**  
Please adapt and extend it responsibly within your SugarCRM environment.
