#----------------------------#
#        QUINN VOICE AGENT
#----------------------------#

"""
Pipeline:

User Voice
↓
Silero VAD       (detect speech start/stop)
↓
Deepgram STT     (speech → text)
↓
Gemini LLM       (google-genai streaming, via GeminiLLM plugin)
↓
Cartesia TTS     (text → speech)
↓
Audio returned to user
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from dotenv import load_dotenv

from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    RunContext,
    cli,
    function_tool,
)
from livekit.plugins import cartesia, deepgram, silero

from google import genai
from google.genai import types as gtypes

from prompts import SYSTEM_PROMPT

load_dotenv()
logger = logging.getLogger("QUINN_AGENT")
logging.basicConfig(level=logging.INFO)

# One Gemini client shared across the process
_gemini_client = genai.Client()


# ---------------------------
# Per-session user data
# ---------------------------
@dataclass
class QuinnData:
    last_entries: list = field(default_factory=list)


# ---------------------------
# Gemini LLM — plugged in via AgentSession(llm=)
# ---------------------------
class GeminiLLM:
    """
    Minimal LLM adapter that AgentSession accepts.
    chat() receives the full conversation and streams text chunks back.
    Uses run_in_executor so the sync Gemini iterator never blocks the event loop.
    """

    def __init__(self, model: str = "gemini-2.0-flash-exp", temperature: float = 0.8):
        self.model = model
        self.temperature = temperature

    async def chat(self, *, chat_ctx, **kwargs):
        contents = _build_gemini_contents(chat_ctx)

        sync_stream = _gemini_client.models.generate_content_stream(
            model=self.model,
            contents=contents,
            config=gtypes.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=self.temperature,
            ),
        )

        loop = asyncio.get_running_loop()
        it = iter(sync_stream)

        async def _stream():
            while True:
                try:
                    chunk = await loop.run_in_executor(None, next, it)
                except StopIteration:
                    break
                if hasattr(chunk, "text") and chunk.text:
                    yield chunk.text
                elif hasattr(chunk, "candidates"):
                    for candidate in chunk.candidates or []:
                        for part in getattr(candidate.content, "parts", []):
                            if hasattr(part, "text") and part.text:
                                yield part.text

        return _stream()


def _build_gemini_contents(chat_ctx) -> list[gtypes.Content]:
    """
    Convert LiveKit ChatContext messages → Gemini Content list.
    Skips system messages (passed via system_instruction).
    Maps assistant → model for Gemini role naming.
    Ensures the last turn is always "user" (Gemini requirement).
    """
    contents: list[gtypes.Content] = []

    for msg in chat_ctx.messages:
        role = msg.role if isinstance(msg.role, str) else msg.role.value
        if role == "system":
            continue
        gemini_role = "model" if role == "assistant" else "user"
        text = (getattr(msg, "content", "") or "").strip()
        if text:
            contents.append(
                gtypes.Content(
                    role=gemini_role,
                    parts=[gtypes.Part(text=text)],
                )
            )

    if not contents or contents[-1].role != "user":
        contents.append(
            gtypes.Content(
                role="user",
                parts=[gtypes.Part(text="Please continue.")],
            )
        )

    return contents


# ---------------------------
# Tools
# ---------------------------
@function_tool
async def log_study_entry(
    context: RunContext,
    subject: str,
    duration_minutes: int,
    mood: str,
    notes: str = "",
):
    """
    Log a completed study session entry.
    Call this once you have confirmed subject, duration, and mood with the student.

    Args:
        subject: The subject or topic studied.
        duration_minutes: How long the student studied in minutes.
        mood: Student's mood — one of: great, okay, rough.
        notes: Any optional extra notes about the session.
    """
    entry = {
        "subject": subject,
        "duration_minutes": duration_minutes,
        "mood": mood,
        "notes": notes,
    }
    logger.info(f"[ENTRY LOGGED] {json.dumps(entry, indent=2)}")

    # --- Persist to your DB here ---
    # await db.insert("study_sessions", entry)

    # Store in session userdata
    context.userdata.last_entries.append(entry)

    return f"Logged: {subject} for {duration_minutes} minutes. Mood: {mood}."


# ---------------------------
# AgentServer + entrypoint
# ---------------------------
server = AgentServer()


@server.rtc_session()
async def entrypoint(ctx: JobContext):
    session = AgentSession(
        vad=silero.VAD.load(),
        stt=deepgram.STT(),
        llm=GeminiLLM(model="gemini-2.0-flash-exp", temperature=0.8),
        tts=cartesia.TTS(),
        userdata=QuinnData(),
    )

    agent = Agent(
        instructions=SYSTEM_PROMPT,
        tools=[log_study_entry],
    )

    await session.start(agent=agent, room=ctx.room)

    await session.generate_reply(
        instructions="Greet the student warmly as QUINN and ask what they studied today."
    )


# ---------------------------
# Run
# ---------------------------
if __name__ == "__main__":
    cli.run_app(server)