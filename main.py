from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from chat import ChatManager, MessageRequest, ResponseMessage
from config.settings import Settings

chat_manager = ChatManager()
app = FastAPI()
settings = Settings()

# Allow frontend CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5501"],  # you can later restrict this
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/chat", response_model=ResponseMessage)
def chat(request: MessageRequest):
    return chat_manager.process_message(message=request.message, language=request.language, sender="human")


@app.get("/config")
def get_config():
    return {
        "software_version": settings.SOFTWARE_VERSION,
    }