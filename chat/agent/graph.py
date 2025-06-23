from typing import Literal

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AnyMessage,AIMessage, SystemMessage, ToolMessage
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt
from termcolor import colored

from chat.agent.prompts import get_system_prompt
from chat.agent.state import AgentState
from chat.agent.tools import (
    check_system_time,
    update_to_do_list
)
from config.settings import Settings
from log_module.log_utils import TimeLogger

VERBOSE = bool(int(Settings.VERBOSE))



def filter_messages(all_messages: list):
    def is_relevant_message(msg: AnyMessage, index: int, total_messages: int):
        # Always keep last 3 messages
        if index >= total_messages - 3:
            return True

        # # Exclude ToolMessage
        # if isinstance(msg, ToolMessage):
        #     return False

        # # Exclude AIMessage with no content
        # if isinstance(msg, AIMessage) and not msg.content:
        #     return False

        # Keep all other messages
        return True

    # Apply custom filtering
    filtered_messages = [
        msg
        for idx, msg in enumerate(all_messages)
        if is_relevant_message(msg, idx, len(all_messages))
    ]
    return filtered_messages


# --------------------------
# BUILD GRAPH
# --------------------------


class Agent:
    def __init__(self, llm: BaseChatModel, language:str, checkpointer):
        # --------------------------
        # BUILD GRAPH
        # --------------------------

        main_graph = StateGraph(AgentState)

        main_graph.add_node("LLM_assistant", self.LLM_node)
        main_graph.add_node("tool_node", self.tool_node)
        main_graph.add_node("final_response_node", self.final_response_node)


        main_graph.add_edge(START, "LLM_assistant")
        main_graph.add_edge("tool_node", "LLM_assistant")

        main_graph.add_edge("final_response_node", END)

        # --------------------------
        # COMPILE GRAPH
        # --------------------------

        self.graph = main_graph.compile(checkpointer=checkpointer, debug=False)

        # --------------------------
        # CONFIGURE LLM MODEL
        # --------------------------

        self.llm = llm

        tools = [
            check_system_time,
            update_to_do_list
        ]

        # Map tool names to tool instances
        self.tool_map = {tool.name: tool for tool in tools}
        self.valid_tool_names = [tool.name for tool in tools]

        self.llm_with_tools = llm.bind_tools(tools)  # MODEL WITH TOOLS
        self.language = language
    # --------------------------
    # NODES
    # --------------------------

    # LLM Assistant Node
    def LLM_node(self, state: AgentState) -> Command[Literal["tool_node", "final_response_node"]]:
        """Assistant node - LLM"""
        
        next_node = "final_response_node"
        
        timelog = TimeLogger(state.get("_timelog", []))

        # Apply custom filtering
        filtered_messages = filter_messages(state["_messages"])

        messages_list = [
            SystemMessage(content=get_system_prompt(cdu="main", language = self.language))
        ] + filtered_messages

        # Call LLM
        timelog.mark("LLM Start")
        ai_message = self.llm_with_tools.invoke(messages_list)
        timelog.mark("LLM End")

        # if VERBOSE:
        #     for i, msg in enumerate(filtered_messages): print(colored(f"{i} : {msg.content}\n", 'light_magenta'))
        #     print(colored(f"\n+ : New AIMessage > \n{message_to_dict(ai_message)["data"]["content"]}", 'light_magenta'))

        # Token count (through LangChain AIMessage)
        token_usage = {
            "input_tokens": ai_message.usage_metadata["input_tokens"],
            "output_tokens": ai_message.usage_metadata["output_tokens"],
        }

        next_node = "tool_node" if ai_message.tool_calls else "final_response_node"
        update = {
            "_messages": [ai_message],
            "_token_usage": token_usage,
            "_timelog": timelog.steps,
        }

        return Command(goto=next_node, update=update)

    # Tool Node
    def tool_node(self, state: AgentState) -> Command:
        """Assistant node - LLM"""
        timelog = TimeLogger(state.get("_timelog", []))

        chat_input = ""
        last_ai_message = state["_messages"][-1]
        sensitive_tools = ["update_to_do_list"]

        for tool_call in last_ai_message.tool_calls:
            tool_message = ToolMessage(tool_call_id=tool_call["id"], content="")

            tool = self.tool_map.get(
                tool_call["name"]
            )  # getting tool instance from the name


            if tool is None:
                tool_message = ToolMessage(
                    tool_call_id=tool_call["id"],
                    content=str(
                        f"[LLM_node WARNING] {tool_call['name']} is not a valid tool. Do not expect a response from it."
                    ),
                )
                error = f"{tool_call['name']} is not a valid tool call."
                print(colored(f"\nTool Error: {error}", "red"))

            else:
                # Interrupt for tool call confirmation
                if tool_call["name"] in sensitive_tools:
                    
                    INTERRUPT_PHRASE = {"EN":"&#x1F6D1; Double confirmation required. Would you like to continue the execution? (type 'yes'):",
                                        "ES": "&#x1F6D1; Se requiere doble confirmación. ¿Desea continuar con la ejecución? (escriba 'yes'):"}
                    
                    chat_input = interrupt(
                        INTERRUPT_PHRASE.get(self.language)
                    )
                    
                if VERBOSE: print(colored(f"\nTool requested: {tool_call}", "green"))

                try:
                    # Alert detection during interrupt
                    if "[alert]" in chat_input.lower():
                        tool_message = ToolMessage(
                            tool_call_id=tool_call["id"],
                            content="An alert interrupted the tool calling.",
                        )
                        raise AlertException()

                    # Tool call confirmed
                    if (tool_call["name"] not in sensitive_tools) or (
                        tool_call["name"] in sensitive_tools
                        and chat_input.lower() == "yes"
                    ):
                        timelog.mark(f"Tool Invoke Start: {tool_call['name']}")
                        command = tool.invoke(
                            input=tool_call,
                            config={
                                "configurable": {
                                    "additional_field": {
                                        k: v
                                        for k, v in state.items()
                                        if not k.startswith("_")
                                    }
                                }
                            },
                        )
                        timelog.mark(f"Tool Invoke End: {tool_call['name']}")

                    # Tool call canceled
                    else:
                        tool_message = ToolMessage(
                            tool_call_id=tool_call["id"],
                            content="The user cancelled the execution.",
                        )
                        command = Command(
                            update={"_messages": [tool_message]}
                        )

                except AlertException:
                    command = Command(
                        update={"_messages": [tool_message]}
                    )

                except Exception as e:
                    print(colored(f"\nTool Error: {e}", "red"))
                    command = Command(
                        update={"_messages": [tool_message]}
                    )

        return command
    
    # LLM Assistant Node
    def final_response_node(self, state: AgentState) -> Command:
        """Assistant node - LLM"""
        
        
        try:
            # Apply custom filtering
            original_ai_message = state["_messages"][-1]

            if not isinstance(original_ai_message, AIMessage):
                raise Exception("The last message is not an AIMessage.")
            if not original_ai_message.content.strip():
                raise Exception("The last AIMessage content is empty.")
            
            
            llm_input = get_system_prompt(cdu='tts', language = self.language, input = original_ai_message.content)
            
             # Call LLM
            response = self.llm.invoke(llm_input)
            tts_string = response.content.strip()
            
        except Exception as e:
            tts_string = ""
            print(colored(f"\nFinal Response Error: {e}", "red"))
        

        update = {
            "_tts_text": tts_string
            }

        return Command(update=update)
