import json
import re
import hashlib
import logging
import io
import csv
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4

def parse_pose_names_from_function_call(function_call):
    try:
        args_str = function_call.get("arguments", "{}")
        args = json.loads(args_str)
        pose_names = args.get("pose_names", [])
        if not isinstance(pose_names, list):
            raise ValueError("pose_names must be a list.")
        return pose_names
    except (json.JSONDecodeError, TypeError, ValueError) as e:
        logger.error(f"Error parsing pose names from function call: {e}")
        return []

def get_yogajournal_pose_image(pose_name: str) -> str:
    """Returns a Yoga Journal URL for the given pose name."""
    slug = re.sub(r'[^a-z0-9]+', '-', pose_name.lower()).strip('-')
    base_url = f"https://www.yogajournal.com/poses/{slug}/"
    return base_url

def extract_pose_names(text: str) -> dict:
    """Extract yoga pose names (English or Sanskrit) mentioned in the input text."""
    # A placeholder simple regex example — you can replace this with something smarter
    possible_poses = re.findall(r'\b[A-Za-z]+\b', text)
    return {"pose_names": possible_poses}

DEFAULT_HOLD_TIMES = {
    "hatha": 30,
    "yin": 180,
    "vinyasa": 5 * 6  # ~5 breaths
}

def create_sequence(params, retriever=None, llm=None, style="hatha"):
    try:
        poses = params.get("poses", [])
        sequence_name = params.get("sequence_name", None)

        if not isinstance(poses, list) or not poses:
            raise ValueError("Invalid or missing 'poses' list.")

        default_hold_time = DEFAULT_HOLD_TIMES.get(style, 30)

        sequence = {
            "sequence_name": sequence_name or f"{style.title()} Yoga Sequence",
            "style": style,
            "poses": [
                {"name": pose.title(), "duration": f"{default_hold_time} seconds"}
                for pose in poses
            ],
            "total_duration": f"{default_hold_time * len(poses)} seconds"
        }

        return sequence

    except Exception as e:
        logger.error(f"Error creating sequence: {e}")
        return {
            "sequence_name": "Error",
            "style": style,
            "poses": [],
            "total_duration": "0 seconds",
            "error": str(e)
        }

_pose_query_cache = set()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

def get_pose_benefits(pose_names, retriever, base_llm):
    if not pose_names:
        return "Please specify which pose(s) you want to know about."

    results = []

    for pose in pose_names:
        try:
            query = f"Tell me the benefits and contraindications of the yoga pose '{pose}'."
            docs = retriever.get_relevant_documents(query)

            if not docs:
                logger.warning(f"No documents found for pose: {pose}")
                results.append(f"### 🧘‍♀️ {pose.title()}\n\nNo information found.")
                continue

            combined_text = "\n\n".join([doc.page_content for doc in docs[:3]])

            prompt = f"""
You are a yoga expert assistant.

Based on the following text about the pose '{pose}', provide a clear, concise summary with four sections:

Description:
- A brief explanation of the pose and its purpose.

How to perform:
- Step-by-step instructions on how to get into the pose safely and correctly.

Benefits:
- List main benefits in bullet points.

Contraindications:
- List main contraindications in bullet points.

Separate the sections with a blank line. Use simple language.

Text:
{combined_text}
"""

            response = base_llm.invoke(prompt)
            # Extract and deduplicate sources
            sources_set = {doc.metadata.get("source", "Unknown source") for doc in docs[:3]}
            sources_list = sorted(sources_set) 

            # Format for display
            sources_text = "\n\n**Sources:**\n" + "\n".join(f"- {src}" for src in sources_list)

            results.append(f"### 🧘‍♀️ {pose.title()}\n\n{response.content.strip()}{sources_text}")

        except Exception as e:
            logger.error(f"Failed to get benefits for pose '{pose}': {e}")
            results.append(f"### 🧘‍♀️ {pose.title()}\n\nAn error occurred while retrieving pose information.")

    return "\n\n".join(results)

# Exporting conversation functions

def format_chat_plain_text(chat_history):
    lines = []
    for role, message in chat_history:
        prefix = "You" if role == "user" else "Yoga GPT"
        lines.append(f"{prefix}: {message}")
    return "\n\n".join(lines)

def format_chat_json(chat_history):
    return json.dumps([{"role": role, "message": message} for role, message in chat_history], indent=2)

def format_chat_csv(chat_history):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["role", "message"])
    for role, message in chat_history:
        writer.writerow([role, message])
    return output.getvalue()

def format_chat_pdf(chat_history):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()

    user_style = ParagraphStyle(
        name="UserStyle", parent=styles["Normal"], fontSize=12, spaceAfter=6, leftIndent=0, textColor="black"
    )
    bot_style = ParagraphStyle(
        name="BotStyle", parent=styles["Normal"], fontSize=11, spaceAfter=10, leftIndent=10, textColor="darkblue"
    )

    flowables = []

    for entry in chat_history:
        if isinstance(entry, tuple):
            role, content = entry
        else:
            role = entry.get("role", "unknown")
            content = entry.get("content", "")

        role = role.lower()
        content = clean_text_for_pdf(content)

        if role == "user":
            para = Paragraph(f"👤 <b>User:</b><br/>{content}", user_style)
        else:
            para = Paragraph(f"🤖 <b>Bot:</b><br/>{content}", bot_style)

        flowables.append(para)
        flowables.append(Spacer(1, 8))

    doc.build(flowables)
    buffer.seek(0)
    return buffer


def clean_text_for_pdf(text):
    """Format raw AI output for nicer display in PDF."""
    # Markdown-like headings → bold
    text = re.sub(r"(?m)^#+\s*(.*)", r"<b>\1</b>", text)

    # Lists
    text = re.sub(r"(?m)^-\s*", r"• ", text)

    # Fix newlines (optional: adjust to keep paragraphs)
    text = text.replace("\n", "<br/>")

    # Convert "n " used in token/cost info into line breaks
    text = re.sub(r"\bn\b", "<br/>", text)

    return text