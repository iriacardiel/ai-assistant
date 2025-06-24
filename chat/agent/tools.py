from langchain_core.tools import tool, InjectedToolCallId
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import ToolMessage
from langgraph.types import Command
from typing import Annotated
from termcolor import colored
import json
from config import Settings
from datetime import datetime
import uuid

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
    
    content = datetime.today().strftime("%Y-%m-%d %H:%M") # e.g., 2025-06-24 13:45
            
    tool_message = ToolMessage(content, tool_call_id=tool_call_id) 

    update = {
        "_messages": [tool_message],
        "check_system_time_result": content,
        "_tools_used" : ["check_system_time"],
    }
    
        
    return Command(update=update)

@tool
def check_to_do_list(tool_call_id: Annotated[str, InjectedToolCallId]) -> Command:
    """Use this tool to check the to-do list items.
    
    Arguments: None
        
    Output:
        - To-do list. Each item is a task.
    """
    
    with open("services/to_do_list/to_do_list.json") as file:
        to_do_list = json.load(file)
    
    content = f"""
    To-do list:
    {json.dumps(to_do_list, indent=2)}
    """
    
    tool_message = ToolMessage(content, tool_call_id=tool_call_id)

    update = {
        "_messages":[tool_message],
        "_tools_used" : ["check_to_do_list"],
    }
    
    return Command(update=update)   

@tool
def update_to_do_list(taskDescription:str, tool_call_id: Annotated[str, InjectedToolCallId]) -> Command:
    """Use this tool to update the to-do list with the new task.
    
    Arguments: 
        - taskDescription:str For example 'Buy milk'
        
    Output:
        - Confirmation of the task saved.
    """
    # Read existing tasks
    with open("services/to_do_list/to_do_list.json") as file:
        to_do_list = json.load(file)

    # Create a new task
    newTask = {
        "taskId": str(uuid.uuid4()),
        "taskDescription": taskDescription,
        "Completed": False,
        "registerDate": datetime.today().strftime("%Y-%m-%d %H:%M"),
        "dueDate": "never"
    }

    # Append new task to the list
    to_do_list.append(newTask) 

    # Write updated list back to file
    with open("services/to_do_list/to_do_list.json", "w") as file:
        json.dump(to_do_list, file, indent=4)
    
    content = f"""
    To-do list updated with task:
    {json.dumps(newTask,indent=2)}
    """
    
    tool_message = ToolMessage(content, tool_call_id=tool_call_id)

    update = {
        "_messages":[tool_message],
        "_tools_used" : ["update_to_do_list"],
    }
    
    return Command(update=update)


        

    



   