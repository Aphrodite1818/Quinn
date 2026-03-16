from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
from prompts import SYSTEM_PROMPT, USER_PROMPT  

load_dotenv()

# Initialize Gemini client
client = genai.Client()

# Ensure USER_PROMPT is a list
contents_list = [USER_PROMPT] if isinstance(USER_PROMPT, str) else USER_PROMPT

# Stream response from Gemini
response_stream = client.models.generate_content_stream(
    model="gemini-3-flash-preview",
    contents=contents_list,
    config=types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT
    )
)

# Print streamed output as it comes
for chunk in response_stream:
    if hasattr(chunk, "text"):
        print(chunk.text, end="")