import os
import sqlite3
from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import Any, Dict, Tuple

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import Command
from termcolor import colored
from chat.agent.graph import Agent
from chat.agent.state import AgentState
from config.settings import Settings
from frontend.format_response import format_display_response, format_tts_response
from tts.TTS import TTSGenerator
from images import generate_images
from log_module.log_utils import (
    TimeLogger,
    log_agent_messages,
    log_agent_state,
    log_token_usage,
)


class ChatSession:
    """Manages an individual chat session."""

    def __init__(self, settings: Settings, memory_db_path: str = "memory/memory.db"):
        self.settings = settings
        self._session_lock = Lock()
        self._memory_db_path = memory_db_path

        # Initialize session state
        self._agent: Agent = None
        self._state: AgentState = None
        self._config: Dict[str, Any] = None
        self._prev_msg_count: int = 0
        self._interrupted: bool = False
        self._new_messages: list = []
        self._timelog: TimeLogger = None
        self._tts_generator = TTSGenerator()

        self._initialize_session()

    def _create_llm(self):
        """Create LLM instance based on configuration."""
        if self.settings.MODEL_SERVER == "OPENAI":
            return ChatOpenAI(
                model=Settings.MODEL_NAME,
                temperature=1,
                api_key=self.settings.OPENAI_API_KEY,
            )
        else:
            return ChatOllama(
                model=Settings.MODEL_NAME, temperature=0, num_ctx=16000, n_seq_max=1
            )

    def _create_memory_checkpointer(self):
        """Create memory checkpointer."""
        conn = sqlite3.connect(database=self._memory_db_path, check_same_thread=False)
        return SqliteSaver(conn)

    def _initialize_session(self, language:str="EN"):
        """Initialize a new chat session."""
        self._delete_previous_data()

        llm = self._create_llm()
        memory = self._create_memory_checkpointer()
        self._agent = Agent(llm=llm, language=language, checkpointer=memory)
        self._state = {"_messages": [], "_timelog": []}
        self._config = {
            "configurable": {
                "thread_id": "thread-"
                + datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            }
        }
        self._prev_msg_count = 0
        self._new_messages = []
        self._interrupted = False
        self._timelog = TimeLogger(self._state.get("_timelog", []))
        self._tts_generator = TTSGenerator(tts_language=language)

        generate_images.draw_mermaid(self._agent.graph)

        if self.settings.VERBOSE:
            print("🟢 SESSION STARTED")

    def _delete_previous_data(self):
        """Clean up previous session data."""
        if self.settings.VERBOSE:
            print("🔄 Restoring session")

        target_folder_names = ["images", "logs", "tts"]
        patterns = ["graph", "log", ".wav"]

        for folder_name in target_folder_names:
            folder = Path(folder_name)
            if folder.exists():
                for file in folder.iterdir():
                    if (
                        file.is_file()
                        and any(p in file.name for p in patterns)
                        and not file.name.endswith(".py")
                    ):
                        os.remove(file)
                        if self.settings.VERBOSE:
                            print(f"🗑️ Deleted: {file}")

    def _extract_messages(self, messages: list) -> Tuple[str, str, str]:
        """Extract different types of messages."""
        ai_messages, tool_messages, system_messages = "", "", ""

        for msg in messages:
            if isinstance(msg, AIMessage) and msg.content.strip():
                ai_messages += f"{msg.content}\n"
            elif isinstance(msg, ToolMessage) and msg.content.strip():
                tool_messages += f"{msg.content}\n"
            elif isinstance(msg, SystemMessage) and msg.content.strip():
                system_messages += f"{msg.content}\n"

        return ai_messages, tool_messages, system_messages

    def _log_session_data(self):
        """Log session data if logging is enabled."""
        state_to_log = {
            k: self._state[k] for k in self._state if k not in ["_messages"]
        }

        if self.settings.LOGGING:
            log_agent_state(state_to_log)
            log_agent_messages(self._new_messages)
            log_token_usage(self._state.get("_token_usage", {}))
            self._timelog.log()

        if self.settings.VERBOSE:

            print(
                colored(
                    f"🔍 Messages count | TOTAL: {len(self._state['_messages'])} | "
                    f"PREVIOUS: {self._prev_msg_count} | NEW: {len(self._new_messages)}",
                    "light_magenta",
                )
            )

    def chat(self, chat_input: str, language:str, sender: str = "human") -> Dict[str, str]:
        """Process a chat input and return response."""
        with self._session_lock:
            ai_messages, tool_messages, system_messages, tts_text, tts_base64 = "", "", "", "", ""

            # Handle session reset
            if chat_input.strip().lower() == "exit":
                self._initialize_session(language=language)
                self._delete_previous_data()
                ai_messages = "Session reset."
            else:
                # Process normal chat
                self._timelog = TimeLogger(self._state.get("_timelog", []))

                if self._interrupted:
                    self._state = self._agent.graph.invoke(
                        Command(resume=chat_input), self._config
                    )
                    self._interrupted = False
                else:
                    if sender == "human":
                        self._state["_messages"].append(HumanMessage(content=chat_input))
                        self._state = self._agent.graph.invoke(self._state, self._config)
                    elif sender == "alert manager":
                        self._state = self._agent.graph.invoke(
                            Command(
                                update={"_messages": HumanMessage(content=chat_input)},
                                goto="LLM_assistant",
                            ),
                            self._config,
                        )

                # Extract new messages
                self._new_messages = self._state["_messages"][self._prev_msg_count :]
                self._prev_msg_count = len(self._state["_messages"])

                ai_messages, tool_messages, system_messages = self._extract_messages(
                    self._new_messages
                )

                # Check for interrupts
                tasks = self._agent.graph.get_state(self._config).tasks
                if tasks:
                    self._interrupted = True
                    interrupt_phrase = tasks[0].interrupts[0].value
                    ai_messages += (
                        f"\n{interrupt_phrase}" if ai_messages else f"{interrupt_phrase}"
                    )
                    tts_text = format_tts_response(interrupt_phrase)
                
                # Get the text-to-speech output 
                tts_text = format_tts_response(self._state.get("_tts_text", "")) if not tts_text else tts_text 
                tts_base64 = self._tts_generator.generate(
                    text=tts_text,
                    save=True,
                )
                 
                self._log_session_data()
                
                print(tts_text)

            return {
                "ai_messages": format_display_response(ai_messages.strip()),
                "tool_messages": tool_messages.strip(),
                "system_messages": system_messages.strip(),
                "tools_used": self._state.get("_tools_used", []),
                "tts_text": tts_text,
                "tts_audio": tts_base64,
            }
