🧘 Yoga Chatbot with Advanced RAG and Function Calling

This Streamlit-based AI chatbot assists users in learning about yoga poses, anatomy, and philosophy. 
It combines Retrieval-Augmented Generation (RAG) with multimodal capabilities like image detection and function calling. 
Built using LangChain, FAISS, and OpenAI tools, it supports structured query translation, context-aware retrieval, and conversational export.


📁 Project Structure
.
```
├── .streamlit/ # Streamlit config & secrets
├── data/ # Source PDFs (Yoga Anatomy, Sutras, etc.)
├── fails_index/ # FAISS indexes
├── app.py # Streamlit app entry point
├── function_schemas.py # Function calling tools for multimodal queries
├── loader.py # PDF loader and splitter
├── poetry.lock
├── pyproject.toml # Poetry dependencies
├── retriever.py # Vectorstore retriever & RAG logic
├── utils.py # Helper functions (formatting, export, etc.)

```
🧪 Features

🔎 Advanced RAG: Uses query translation, filtering, and structured retrieval

🤖 Function calling: Detect poses and provide guided responses

💬 Chat export: Export conversations as TXT, CSV, or JSON

🧘‍♀️ Yoga sources: Includes structured content from trusted yoga manuals

📚 Modular & Clean: Code split into utilities and schemas



🚀 Local Development (with Poetry)

1. Clone the repo
```
git clone https://github.com/TuringCollegeSubmissions/anaisp-AE.2.5
cd anaisp-AE.2.5
```

4. Install Poetry dependencies
```
poetry install
```

5. Activate the virtual environment
```
poetry shell
```

6. Run the app
```
streamlit run app.py
```

☁️ Deploying to Render (Cloud)

1. Set up a new Render Web Service

2. Set the following configurations:
  
Build Command:
```
pip install -r requirements.txt
```
   
Start Command: 
```
streamlit run app.py --server.port 10000
```
Runtime: Python 3.10+
Instance Type: Starter or above

3. API key


To run this app, you'll need to create a .env file in the root of the project and include your OpenAI API
```
touch .env
```

Then add the following line to it:
```
OPENAI_API_KEY=your_openai_api_key_here
```
Make sure you have your OpenAI API key ready. The app uses this to connect to GPT-4 for answering questions.


4. Push to GitHub and connect Render
Make sure your GitHub repo includes:
requirements.txt (exported from Poetry for Render)
app.py in the root directory
Then deploy via Render’s web dashboard.

🖼 Screenshot


📬 How to Use
Ask the bot about a yoga pose, anatomy, or philosophy.
Export your chat in your chosen format.
Enjoy exploring yoga with intelligent guidance 🌿


