import os

from dotenv import load_dotenv  # pip install python-dotenv

load_dotenv()


class Settings:
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    VERBOSE = os.environ.get("VERBOSE")
    VERBOSE_LLM = os.environ.get("VERBOSE_LLM")
    LOGGING = os.environ.get("LOGGING")
    MODEL_SERVER = os.environ.get("MODEL_SERVER")
    MODEL_NAME = os.environ.get("MODEL_NAME")
    SOFTWARE_VERSION = os.environ.get("SOFTWARE_VERSION")
    LETTA_API_KEY = os.environ.get("LETTA_API_KEY")
