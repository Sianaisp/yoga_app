import json
import logging
import warnings
import time
import io
import streamlit as st
from retriever import build_qa_chain
from streamlit.runtime.scriptrunner import RerunException, RerunData
from langchain_community.chat_models import ChatOpenAI
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import HumanMessage, SystemMessage
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain

from utils import (
    parse_pose_names_from_function_call,
    get_pose_benefits,
    create_sequence,
    get_yogajournal_pose_image,
    extract_pose_names,
    format_chat_plain_text,
    format_chat_json,
    format_chat_csv,
    format_chat_pdf
)
from function_schemas import (
    pose_detection_function,
    create_sequence_function,
    get_pose_benefits_function,
    get_yogajournal_pose_image_function
)

warnings.filterwarnings("ignore", message=".*LangChainDeprecationWarning.*")
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger("langchain").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)
st.set_page_config(page_title="Yoga GPT", page_icon="🧘‍♀️", layout="wide")
st.title("🧘 Yoga GPT - Your Personal Yoga Assistant")

# Initialize LLM and embeddings
llm_model = "gpt-4"

retriever, query_rewrite_chain = build_qa_chain()

base_llm = query_rewrite_chain.llm

# Sidebar settings
st.sidebar.markdown("## Chat Settings")
style = st.sidebar.selectbox("Yoga Style for Sequences:", ["hatha", "yin", "vinyasa"])
show_images = st.sidebar.checkbox("Show Pose Images from Yoga Journal", value=True)

SYSTEM_PROMPT = (
    """
    You are a knowledgeable and supportive yoga assistant.

    Your primary goal is to provide informative, high-quality responses about yoga poses and sequences.

    ✅ When the user asks about a yoga pose (e.g., "what’s a good hip opener", "tell me about pigeon pose"):
    - Always call get_pose_benefits first to retrieve detailed textual information.
    - Include benefits, contraindications, alignment cues, and any relevant tips in your response.
    - Only call get_yogajournal_pose_image after get_pose_benefits to optionally enhance your response with an image.
    - Never call get_yogajournal_pose_image on its own, and never return an image or link without context or explanation.

    ✅ When the user asks for a full sequence (e.g., "give me a morning flow", "make me a yin yoga hip sequence"):
    - Call create_sequence, using the selected style if available (e.g., hatha, yin).
    - Do not use create_sequence for single-pose queries.

    🔁 If multiple functions are needed:
    - Always call get_pose_benefits first.
    - Then call get_yogajournal_pose_image if a visual is appropriate.

    🧠 Your responses should always prioritise being helpful and informative. Think like a thoughtful yoga teacher, not a search engine or image bot.

    🖼️ When including images, embed the image URL naturally at the end of your explanation or in parentheses after describing the pose.

    Never leave your answer as only a link or image. Your job is to teach, guide, and inspire.
    """
)

def format_sequence_output(sequence):
    output = f"🧘‍♀️ **{sequence['sequence_name']}** ({sequence['style'].title()})\n\n"
    for i, pose in enumerate(sequence["poses"], 1):
        output += f"- Step {i}: {pose['name']} — hold for {pose['duration']}.\n"
    output += f"\n🕒 Total Duration: {sequence['total_duration']}"
    return output

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

def display_chat():
    for role, message in st.session_state.chat_history:
        if role == "user":
            st.markdown(f"**You:** {message}")
        else:
            st.markdown(f"**Yoga GPT:** {message}")

display_chat()

# Option to export conversation history
if st.session_state.get("chat_history"):

    st.markdown("### Export conversation:")

    chat_history = st.session_state.chat_history

    txt_data = format_chat_plain_text(chat_history)
    st.download_button(
        label="Download as TXT",
        data=txt_data,
        file_name="yoga_gpt_chat_history.txt",
        mime="text/plain",
    )

    json_data = format_chat_json(chat_history)
    st.download_button(
        label="Download as JSON",
        data=json_data,
        file_name="yoga_gpt_chat_history.json",
        mime="application/json",
    )

    csv_data = format_chat_csv(chat_history)
    st.download_button(
        label="Download as CSV",
        data=csv_data,
        file_name="yoga_gpt_chat_history.csv",
        mime="text/csv",
    )

    chat_history = [{"role": role, "content": content} for role, content in chat_history]
    pdf_buffer = format_chat_pdf(chat_history)
    st.download_button(
        label="Download as PDF",
        data=pdf_buffer,
        file_name="yoga_gpt_chat_history.pdf",
        mime="application/pdf",
    )

with st.form(key="user_input_form", clear_on_submit=True):
    user_input = st.text_area("Your message:", height=80, placeholder="Ask your yoga question or request a sequence...")
    submit = st.form_submit_button("Send")

if submit and user_input.strip():
    # 🔒 Rate limiting: allow only 1 query every 10 seconds
    if "last_query_time" not in st.session_state:
        st.session_state["last_query_time"] = 0

    current_time = time.time()
    if current_time - st.session_state["last_query_time"] < 10:
        st.warning("You're sending requests too fast. Please wait a few seconds.")
        st.stop()

    # Update the time only after passing the check
    st.session_state["last_query_time"] = current_time
    st.session_state.chat_history.append(("user", user_input.strip()))

    # NEW: Run query rewriting on raw user input first
    rewritten_query = query_rewrite_chain.run(user_input.strip())
    logging.debug(f"Rewritten query: {rewritten_query}")

    # Build messages with rewritten query instead of raw user input
    messages = [SystemMessage(content=SYSTEM_PROMPT)]
    # Include all previous chat history except the last user input (because we use rewritten)
    for role, msg in st.session_state.chat_history[:-1]:
        if role == "user":
            messages.append(HumanMessage(content=msg))
        else:
            messages.append(SystemMessage(content=msg))
    # Add the rewritten query as the last user message
    messages.append(HumanMessage(content=rewritten_query))

    # Call LLM with function calling (unchanged)
    response = base_llm(
        messages=messages,
        functions=[pose_detection_function, create_sequence_function, get_pose_benefits_function, get_yogajournal_pose_image_function],
        function_call="auto"
    )

    bot_reply = ""
    pose_names = []

    if response.additional_kwargs.get("function_call"):
        func_call = response.additional_kwargs["function_call"]
        func_name = func_call["name"]
        logging.debug(f"Function called: {func_name}")
        with st.spinner("🤖 Thinking deeply about your yoga request..."):

            if func_name == "extract_pose_names":
                pose_names = parse_pose_names_from_function_call(func_call)
                bot_reply = get_pose_benefits(pose_names, retriever, base_llm)

            elif func_name == "get_pose_benefits":
                args = func_call.get("arguments", "{}")
                pose_names = json.loads(args).get("pose_names", [])
                bot_reply = get_pose_benefits(pose_names, retriever, base_llm)

            elif func_name == "get_yogajournal_pose_image":
                args = func_call.get("arguments", "{}")
                pose_name = json.loads(args).get("pose_name", "")
                pose_names = [pose_name]
                bot_reply = ""  # Don’t just say “Fetching image...” — leave blank here

            elif func_name == "create_yoga_sequence":
                args = func_call.get("arguments", "{}")
                sequence_args = json.loads(args)
                sequence_dict = create_sequence(sequence_args, retriever, base_llm, style=style)
                bot_reply = format_sequence_output(sequence_dict)

        # Add Yoga Journal links only if pose_names is set and show_images is True
        if pose_names and show_images:
            links = "\n\n".join(
                [f"[See {pose.title()} on Yoga Journal]({get_yogajournal_pose_image(pose)})" for pose in pose_names]
            )
            bot_reply += f"\n\n{links}"

    else:
        bot_reply = response.content

    # ✅ Token usage and cost estimate — append to bot_reply so it shows in chat
    usage = response.response_metadata.get("token_usage", {})
    if usage:
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        total_tokens = usage.get("total_tokens", 0)

        # GPT-4 pricing (adjust if using gpt-4-turbo or gpt-4o)
        cost = (prompt_tokens / 1000) * 0.03 + (completion_tokens / 1000) * 0.06

        token_info = (
            f"\n\n🧾 **Token usage:** {total_tokens} tokens "
            f"(Prompt: {prompt_tokens}, Completion: {completion_tokens})  \n"
            f"💸 **Estimated cost:** ${cost:.4f}"
        )
        bot_reply += token_info

    st.session_state.chat_history.append(("bot", bot_reply))
    raise RerunException(RerunData())

st.markdown("---")
st.markdown("*Yoga GPT uses knowledge from yoga manuals, books, and anatomy references.*")