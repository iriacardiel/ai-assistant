from pydantic import BaseModel


class MessageRequest(BaseModel):
    """Request model for chat messages."""

    message: str
    language: str = "EN"


class ResponseMessage(BaseModel):
    """Response model for chat messages."""

    ai_messages: str
    tool_messages: str
    system_messages: str
    tools_used: list
    tts_text: str
    tts_audio: str
