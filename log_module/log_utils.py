import csv
import json
import os
from datetime import datetime
from langchain_core.messages import message_to_dict, BaseMessage
import tiktoken
import time
import logging
from termcolor import colored

def log_token_usage(token_usage: dict, timestamp: str = None):
    if timestamp is None:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    file_path = "log_module/token_usage_log.csv"
    file_exists = os.path.exists(file_path)

    with open(file_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["timestamp", "input_tokens", "output_tokens", "total_tokens"])
        total = token_usage.get("input_tokens", 0) + token_usage.get("output_tokens", 0)
        writer.writerow([timestamp, token_usage.get("input_tokens", 0), token_usage.get("output_tokens", 0), total])
        
def log_agent_messages(new_messages: list):
    file_path = "log_module/agent_messages_log.txt"

    with open(file_path, "a", encoding="utf-8") as log_file:
        for message in new_messages:
            agent_message_entry = json.dumps(message_to_dict(message))
            log_file.write("\n" + "=" * 50 + "\n")
            log_file.write(f"🕒 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            log_file.write("=" * 50 + "\n")
            log_file.write(agent_message_entry + "\n")
            
            
def log_agent_state(state: dict):
    file_path = "log_module/agent_state_log.txt"
    try:
        with open(file_path, "a", encoding="utf-8") as log_file:
            log_file.write("\n" + "=" * 50 + "\n")
            log_file.write(f"🕒 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            log_file.write("=" * 50 + "\n")
            log_file.write(json.dumps(state, indent=2) + "\n")
    except Exception as e:
        #print(f"State could not be logged: {e}")
        pass
        

def count_tokens(messages: list[BaseMessage], model_name: str = "gpt-4o") -> int:
        try:
            encoding = tiktoken.encoding_for_model(model_name)
        except KeyError:
            # fallback for unknown models
            encoding = tiktoken.get_encoding("cl100k_base")

        tokens_per_message = 3  # base count per message for GPT-4o-like models
        tokens_per_name = 1     # if 'name' is present in AIMessage, etc.
        total_tokens = 0

        for message in messages:
            total_tokens += tokens_per_message
            for key, value in message_to_dict(message)["data"].items():
                if key == "name":
                    total_tokens += tokens_per_name
                elif isinstance(value, str):
                    total_tokens += len(encoding.encode(value))

        total_tokens += 3  # every reply is primed with <|start|>assistant
        return total_tokens
    
    

"""logging.basicConfig(
    format='[%(asctime)s] %(levelname)s: %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)"""

class TimeLogger:
    def __init__(self, log_steps: list):
        self.steps = log_steps
        self._last_time = self.steps[-1]["_raw_time"] if self.steps else None
        self._last_logged_index = len(self.steps)
        
    def mark(self, label):
        now = time.time()
        wall_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if self._last_time is None:
            delta = 0.0
        else:
            delta = now - self._last_time

        self._last_time = now
        self.steps.append({
            "label": label,
            "timestamp": wall_time,
            "delta": delta,
            "_raw_time": now  # ✅ Needed for future delta calculations
        })

        #logging.info(f"{label} (+{delta:.3f}s)")

    def report(self):
        print(colored("\n📋 Step Timing Summary:", "light_magenta"))
        for i, step in enumerate(self.steps):
            print(colored(f"[{step['timestamp']}] {i} {step['label']:<30} (+{step['delta']:.3f}s)", "light_magenta"))
            
    def log(self):
        file_path = "log_module/time_log.csv"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        file_exists = os.path.exists(file_path)
        with open(file_path, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(["label", "timestamp", "delta", "_raw_time"])

            for step in self.steps[self._last_logged_index:]:
                writer.writerow([
                    step["label"],
                    step["timestamp"],
                    step["delta"],
                    step["_raw_time"]
                ])

        # Update tracker
        self._last_logged_index = len(self.steps)

    def total_time(self):
        return sum(step["delta"] for step in self.steps)