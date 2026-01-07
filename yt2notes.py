from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi
from google import genai
from pdfitdown.pdfconversion import Converter
import re
import os
import requests
import html

# -------------------------------------------------
# CONFIG
# -------------------------------------------------
GEMINI_API_KEY = "Your API Key Here"
GEMINI_MODEL = "gemini-2.5-flash"

# -------------------------------------------------
# HELPER: GET TITLE & SANITIZE
# -------------------------------------------------
def get_video_title(url):
    """Fetches the video title from the YouTube page."""
    try:
        # User-Agent is required to avoid 429/403 errors from YouTube
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        
        # Extract content inside <title> tags
        matches = re.findall(r'<title>(.*?)</title>', response.text)
        if matches:
            # Unescape HTML entities (e.g. &amp; -> &) and remove " - YouTube" suffix
            title = html.unescape(matches[0])
            return title.replace(" - YouTube", "")
            
    except Exception as e:
        print(f"Warning: Could not fetch title ({e}). Using default name.")
    
    return "video_transcript"

def sanitize_filename(name):
    """Removes illegal characters for filenames."""
    # Remove characters that are invalid in file paths
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    # Replace whitespace with underscores (optional, but safer)
    name = name.strip().replace(" ", "_")
    return name

# -------------------------------------------------
# STEP 1: EXTRACT VIDEO ID
# -------------------------------------------------
def extract_video_id(url):
    parsed = urlparse(url)

    if "youtu.be" in parsed.netloc:
        return parsed.path.lstrip("/")

    query = parse_qs(parsed.query)
    if "v" in query:
        return query["v"][0]

    if "/shorts/" in parsed.path:
        return parsed.path.split("/shorts/")[1].split("?")[0]

    if "/embed/" in parsed.path:
        return parsed.path.split("/embed/")[1].split("?")[0]

    raise ValueError("Unsupported YouTube URL format")


# -------------------------------------------------
# STEP 2: EXTRACT SUBTITLES
# -------------------------------------------------
def extract_subtitles(video_id):
    # Note: Ensure this matches your specific library version usage
    ytt_api = YouTubeTranscriptApi()
    fetched_transcript = ytt_api.fetch(video_id)

    lines = []
    for snippet in fetched_transcript:
        text = snippet.text.replace("\n", " ").strip()
        if text:
            lines.append(text)

    return " ".join(lines)


# -------------------------------------------------
# STEP 3: CLEAN TRANSCRIPT
# -------------------------------------------------
def clean_transcript(text):
    text = re.sub(r"\[.*?\]", "", text)
    text = text.replace("♪", "")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# -------------------------------------------------
# STEP 4: CHUNK TRANSCRIPT
# -------------------------------------------------
def chunk_text(text, max_words=1000):
    words = text.split()
    return [
        " ".join(words[i:i + max_words])
        for i in range(0, len(words), max_words)
    ]


# -------------------------------------------------
# STEP 5: GEMINI → NOTION STRUCTURE
# -------------------------------------------------
def gemini_notion_structure(chunk, part, total):
    client = genai.Client(api_key=GEMINI_API_KEY)

    prompt = f"""
Convert the following video transcript into a
Notion-ready structured document.

STRICT RULES:
- Use ONLY the transcript content
- Markdown format
- Clear headings (##, ###)
- Bullet points
- No emojis
- Professional, educational tone
- No hallucinations

Transcript chunk ({part}/{total}):

\"\"\"
{chunk}
\"\"\"

Return clean Markdown only.
"""

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt
    )

    return response.text


# -------------------------------------------------
# EXECUTION
# -------------------------------------------------
if __name__ == "__main__":

    url = input("Enter YouTube URL: ").strip()

    print("Extracting video ID...")
    video_id = extract_video_id(url)
    
    print("Fetching video title...")
    raw_title = get_video_title(url)
    clean_filename = sanitize_filename(raw_title) + ".md"
    print(f"Target Filename: {clean_filename}")

    print("Fetching subtitles...")
    raw_subs = extract_subtitles(video_id)

    print("Cleaning transcript...")
    cleaned_subs = clean_transcript(raw_subs)

    print("Chunking transcript...")
    chunks = chunk_text(cleaned_subs)

    print(f"\nTotal chunks: {len(chunks)}\n")

    final_notes = []

    for i, chunk in enumerate(chunks, start=1):
        print(f"Structuring chunk {i}/{len(chunks)} with Gemini...")
        md = gemini_notion_structure(chunk, i, len(chunks))
        final_notes.append(md)

    with open(clean_filename, "w", encoding="utf-8") as f:
        f.write("\n\n".join(final_notes))

    print("\nDONE")
    print(f"Notion-ready file saved as: {clean_filename}")

    # Use the converter
    converter = Converter()
    converter.convert(
    file_path= clean_filename, 
    output_path= clean_filename + ".pdf", 
    title="YouTube Video Summary"
    )

    print("PDF successfully generated!")
