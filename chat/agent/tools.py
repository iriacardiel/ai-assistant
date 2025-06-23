from langchain_core.tools import tool, InjectedToolCallId
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import ToolMessage
from langgraph.types import Command
from typing import Annotated
from termcolor import colored
import json
from config import Settings

# --------------------------
# TOOLS
# --------------------------   

@tool
def check_system_time(tool_call_id: Annotated[str, InjectedToolCallId]) -> Command:
    """
    Use this tool to check the system time.
    Arguments: None
        
    Output:
        - System time.
    """
    
    content = "10:00"
            
    tool_message = ToolMessage(content, tool_call_id=tool_call_id) 

    update = {
        "_messages": [tool_message],
        "check_system_time_result": content,
        "_tools_used" : ["check_system_time"],
    }
    
        
    return Command(update=update)

    

@tool
def update_to_do_list(task:str, tool_call_id: Annotated[str, InjectedToolCallId]) -> Command:
    """Use this tool to update the to-do list with the new task.
    
    Arguments: 
        - task:str For example 'Buy milk'
        
    Output:
        - Confirmation of the task saved.
    """

    
    content = f"""
    To-do list updated with task {task}
    """
    tool_message = ToolMessage(content, tool_call_id=tool_call_id)

    update = {
        "_messages":[tool_message],
        "last_task": task,
        "_tools_used" : ["get_battlefield_data"],
    }
    
    return Command(update=update)


        

    



   