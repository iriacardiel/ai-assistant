from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
from typing import TypedDict, List, Annotated


def add(left, right):
    """Can also import `add` from the `operator` built-in."""
    if left != right:
        return left + right
    else:
        return left + [None]

# --------------------------
# STATE
# --------------------------
class TokenUsage(TypedDict):
    input_tokens : int
    output_tokens : int
    
# State:
class AgentState(TypedDict, total = False):
    _messages : Annotated[List[AnyMessage], add_messages]
    _token_usage: TokenUsage
    _timelog: list[dict]
    _tools_used: Annotated[list[str], add]
    _tts_text: str
    check_system_time_result: str
    last_task: str
    
    

    
    