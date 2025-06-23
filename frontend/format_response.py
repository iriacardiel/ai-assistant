import re
from config import Settings
import markdown
from markdown.extensions import Extension
import textwrap
from termcolor import colored

VERBOSE_LLM = bool(int(Settings.VERBOSE_LLM))


class ChiCharacterFilter:
    def __init__(self):
        # Define Ch character ranges (CJK Unified Ideographs)
        self.chi_pattern = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff]')
        
    def remove_chi(self, text):
        """Remove only chi characters, keep other non-ASCII (like accented letters)"""
        return self.chi_pattern.sub('', text)
    
    def detect_chi(self, text):
        """Detect if text contains chi characters"""
        return bool(self.chi_pattern.search(text))
    
    def get_chi_ratio(self, text):
        """Get ratio of chi characters to total characters"""
        if not text:
            return 0.0
        chi_chars = len(self.chi_pattern.findall(text))
        return chi_chars / len(text)
    
    def filter_text(self, text):
        """
        Main filtering function
        
        Args:
            text (str): Input text to filter
                    
        Returns:
            str: Filtered text
        """
        if not self.detect_chi(text):
            return text
        
        chi_ratio = self.get_chi_ratio(text)
        print(f"Chi characters: {chi_ratio:.2%} ")

        filtered = self.remove_chi(text)
        
        return filtered



def format_display_response(text: str = "") -> str:
    
    # Clean LLM output
    text = ChiCharacterFilter().filter_text(text)
    
    # Convert LLM output from Markdown to HTML
    text=textwrap.dedent(text)
    text = text.strip()
    
    # “promote” any line that starts with exactly 2 spaces + dash into a 4-space indent, which Markdown will treat as a nested list
    text = re.sub(
        r'(?m)^  -',      # two spaces then a dash, at start of line
        '    -',          # replace with four spaces + dash
        text
    )
    
    # Optional: post-process custom tags like <think>...</think>
    if VERBOSE_LLM:
        text = re.sub(
            r"<think>(.*?)</think>",
            r'<span style="color:cyan; font-size:small;"><em>\1</em></span>',
            text,
            flags=re.DOTALL
        )
    else:
        text = re.sub(r"<think>(.*?)</think>", r'', text, flags=re.DOTALL).strip("\n")
        
    # Convert Markdown to HTML
    html = markdown.markdown(
        text,
        extensions=[
            'markdown.extensions.fenced_code',  # For code blocks
            'markdown.extensions.tables',       # For tables
            'markdown.extensions.nl2br',        # Converts newlines to <br>
            'markdown.extensions.sane_lists',   # Better list handling
        ]
    )

    return html


def format_tts_response(text: str = "") -> str:

    
    text = re.sub(r"<think>(.*?)</think>", r'', text, flags=re.DOTALL).strip("\n")
    text = text.replace("*", "")
    text = text.replace("\u26a0\ufe0f", "") 
    text = text.replace("&#x1F6D1;", "")

    return text



if __name__ == "__main__":
    
    # Quick test
    print("\n=== Quick Integration Test ===")
    sample_output = "Hello! 你好 This is a test 测试 of the filtering system."
    cleaned = ChiCharacterFilter().filter_text(sample_output)
    print(f"Original: {sample_output}")
    print(f"Cleaned: {cleaned}")