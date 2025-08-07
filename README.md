🧘 Yoga Chatbot with Advanced RAG and Function Calling
This Streamlit-based AI chatbot assists users in learning about yoga poses, anatomy, and philosophy. It combines Retrieval-Augmented Generation (RAG) with multimodal capabilities like image detection and function calling. Built using LangChain, FAISS, and OpenAI tools, it supports structured query translation, context-aware retrieval, and conversational export.
📁 Project Structure
.
├── .streamlit/             # Streamlit config & secrets
├── data/                   # Source PDFs (Yoga Anatomy, Sutras, etc.)
├── fails_index/            # FAISS indexes
├── app.py                  # Streamlit app entry point
├── function_schemas.py     # Function calling tools for multimodal queries
├── loader.py               # PDF loader and splitter
├── poetry.lock
├── pyproject.toml          # Poetry dependencies
├── retriever.py            # Vectorstore retriever & RAG logic
├── utils.py                # Helper functions (formatting, export, etc.)
🧪 Features
🔎 Advanced RAG: Uses query translation, filtering, and structured retrieval
🤖 Function calling: Detect poses and provide guided responses
💬 Chat export: Export conversations as TXT, CSV, or JSON
🧘‍♀️ Yoga sources: Includes structured content from trusted yoga manuals
📚 Modular & Clean: Code split into utilities and schemas
🚀 Local Development (with Poetry)
1. Clone the repo
git clone https://github.com/TuringCollegeSubmissions/anaisp-AE.2.5
cd yoga-rag-chatbot
2. Install Poetry dependencies
poetry install
3. Activate the virtual environment
poetry shell
4. Run the app
streamlit run app.py
☁️ Deploying to Render (Cloud)
1. Set up a new Render Web Service
Build Command: pip install -r requirements.txt
Start Command: streamlit run app.py --server.port 10000
Runtime: Python 3.10+
Instance Type: Starter or above
2. Add secrets to .streamlit/secrets.toml
You can set your API keys securely:
[api_keys]
openai_api_key = "your-openai-key"
3. Push to GitHub and connect Render
Make sure your GitHub repo includes:
requirements.txt (exported from Poetry for Render)
app.py in the root directory
Then deploy via Render’s web dashboard.
🖼 Screenshot

For example, showing the export feature or a yoga pose conversation
📬 How to Use
Ask the bot about a yoga pose, anatomy, or philosophy.
Optionally upload a yoga pose image for feedback (if function calling is enabled).
Export your chat from the sidebar.
Enjoy exploring yoga with intelligent guidance 🌿