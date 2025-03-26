import streamlit as st
from streamlit.components.v1 import html

class ChatInput:
    """A styled live text input component with character counter, warning banner, and submit button."""

    def __init__(self, char_limit: int = 200, height: int = 260):
        self.char_limit = char_limit
        self.height = height

    def render(self) -> str:
        """Render the HTML/CSS/JS and return the submitted text value (as a str)."""
        result = html(self._html(), height=self.height)
        # html() sometimes returns a DeltaGenerator instead of the user’s text,
        # so only return it if it’s really a string.
        return result if isinstance(result, str) else ""



    def _html(self) -> str:
        return f"""
        <style>
            .input-card {{ width:100%; max-width:600px; padding:20px; border-radius:12px; box-shadow:0 4px 12px rgba(0,0,0,0.1); background:#fff; font-family:'Inter',sans-serif; }}
            .input-card textarea {{ width:100%; height:100px; padding:12px; font-size:16px; border:1px solid #ccc; border-radius:8px; resize:none; }}
            .input-footer {{ display:flex; justify-content:space-between; align-items:center; margin-top:10px; }}
            #char_count {{ font-size:14px; color:#555; }}
            #warning {{ display:none; font-size:14px; padding:8px; border-radius:6px; margin-top:8px; }}
            #submit {{ padding:10px 24px; border:none; border-radius:8px; background-color:#004C97; color:#fff; font-size:16px; cursor:pointer; }}
            #submit:hover {{ background-color:#003a7a; }}
        </style>
        <div class="input-card">
            <textarea id="text_area" placeholder="Type your policy question here..."></textarea>
            <div id="warning"></div>
            <div class="input-footer">
                <span id="char_count">0/{self.char_limit}</span>
                <button id="submit">Submit</button>
            </div>
        </div>
        <script>
            const ta = document.getElementById('text_area');
            const cc = document.getElementById('char_count');
            const warn = document.getElementById('warning');
            const submitBtn = document.getElementById('submit');
            const limit = {self.char_limit};

            function showWarning(text, isError=false) {{
                warn.style.display = 'block';
                warn.style.backgroundColor = isError ? '#ffcccc' : '#fff4cc';
                warn.style.color = isError ? '#a94442' : '#8a6d3b';
                warn.innerText = text;
            }}

            ta.addEventListener('input', () => {{
                const count = ta.value.length;
                cc.innerText = `${{count}}/${{limit}}`;
                if (count > limit) showWarning(`Your question is ${{count}} characters — please shorten to ${{limit}}.`);
                else warn.style.display = 'none';
            }});

            submitBtn.onclick = () => {{
                const count = ta.value.length;
                if (count > limit) showWarning(`Cannot submit: ${{count}} characters exceeds limit of ${{limit}}.`, true);
                else {{ warn.style.display = 'none'; window.parent.postMessage({{isStreamlitMessage:true, type:'streamlit:setComponentValue', value: ta.value}}, '*'); }}
            }};
        </script>
        """