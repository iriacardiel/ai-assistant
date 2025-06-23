from typing import Any, Dict

from chat.models import ResponseMessage
from config.settings import Settings

from .session import ChatSession


class ChatManager:
    """Manages chat sessions."""

    def __init__(self, settings: Settings = Settings()):
        self.settings = settings
        self._session = ChatSession(settings)


    def process_message(self, message: str, language:str="en", sender: str = "human") -> Dict[str, Any]:
        """Process a chat message."""
        return self._session.chat(message, language, sender)

    def reset_session(self):
        """Reset the current session."""
        self._session = ChatSession(self.settings)


    

    
            
