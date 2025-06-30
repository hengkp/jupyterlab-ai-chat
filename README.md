# jupyterlab-ai-chat

A JupyterLab extension that adds an **AI Chat** entry to the Launcher under the **Other** category. Each click opens a standalone `.aichat` notebook-like file where you can:

* 🧠 Select from local LLMs (e.g. typhoon2‑t1‑3b, Phi‑4, DeepSeek‑R1, Llama, Flan, Qwen, unsloth, openai)
* ⚙️ Tweak generation parameters: `temperature`, `top_p`, `max_tokens`
* 🔎 Toggle **Deep Research Mode** (internet-enabled lookup)
* 📁 Upload documents/images for context
* 💾 Save and continue multi-turn conversations per file

All models live in `/mnt/sisplockers/models` (permission 777) so every user can access them.

---

## 📦 Repository Structure

```
jupyterlab_ai_chat_extension/
├── README.md              # This file
├── setup.py               # Server extension installer
├── package.json           # Frontend extension metadata
├── tsconfig.json          # TypeScript compiler settings
├── style/
│   └── index.css          # CSS overrides
├── aichat_server/
│   └── extension.py       # FastAPI chat proxy
├── model_handlers.py      # (Optional) custom model utilities
└── src/
    ├── index.ts           # React widget entry
    └── plugin.ts          # JupyterLab plugin registration
```

---

## 🚀 Features

* **Per-chat file**: each session is its own file (`.aichat`), exportable and shareable
* **Model picker**: choose any local model from `/mnt/sisplockers/models`
* **Parameter controls**: sliders/inputs for core LLM sampling settings
* **Deep Research**: route queries through DuckDuckGo (or any configured proxy) for live facts
* **File uploads**: attach docs/images to enrich context
* **No GPU needed**: CPU-only inference via `transformers` + `torch`

---

## ⚙️ Prerequisites

* **OS**: Ubuntu 22.04 LTS
* **Python**: via Conda at `/opt/miniconda3`
* **Node.js**: for building frontend
* **JupyterLab** ≥ 3.0
* **Python packages**:

  * `jupyterlab`
  * `jupyter_server`
  * `jupyter_server_proxy`
  * `fastapi`
  * `uvicorn`
  * `transformers`
  * `torch`

---

## 🛠️ Installation

1. **Clone**

   ```bash
   git clone https://github.com/your-org/jupyterlab-ai-chat-launcher.git
   cd jupyterlab-ai-chat-launcher
   ```

2. **Server Extension**

   ```bash
   source /opt/miniconda3/bin/activate python3
   pip install -e .
   jupyter serverextension enable --py jupyterlab_ai_chat
   ```

3. **Frontend Extension**

   ```bash
   npm install
   npm run build
   jupyter labextension install .
   jupyter lab build
   ```

4. **Launch**

   ```bash
   jupyter lab
   ```

You should now see **AI Chat** under **Other** in the launcher.

---

## 🧪 Development

* **Watch & rebuild TS**: `npm run watch`
* **Reinstall**: after code changes, rerun `pip install -e .` and `npm run build`
* **Server logs**: FastAPI via `uvicorn`: check console for errors

---

## 📝 Configuration

* **Models directory**: set `MODEL_DIR` in `aichat_server/extension.py` to point at `/mnt/sisplockers/models`
* **Permissions**: ensure `chmod -R 777 /mnt/sisplockers/models`
* **Port**: default chat proxy on `127.0.0.1:8888`

