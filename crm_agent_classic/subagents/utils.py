"""Shared utilities for agent callbacks."""
import re
from typing import Any, Optional
from google.genai import types


def extract_sql_from_text(text: str) -> str:
    """Extract raw SQL from text, handling markdown blocks and explanations."""
    if not text: return ""
    
    # Try to find markdown code blocks first
    m = re.search(r"```(?:sqlite|sql)?\s*(.*?)\s*```", text, re.DOTALL | re.I)
    s = m.group(1).strip() if m else text.strip()
    
    # If no markdown, try to find a SELECT statement
    if not m:
        x = re.search(r"(SELECT\s+.*)", s, re.DOTALL | re.I)
        s = x.group(1).strip() if x else s.strip("`").strip()
        
    # Ensure it ends with semicolon
    if ";" in s: s = s.split(";")[0] + ";"
    if s and not s.endswith(";"): s += ";"
    
    return s

def clean_sql_output(callback_context: Any, llm_response: Any, **kwargs: Any) -> Any:
    """Callback wrapper: Clean and format SQL output from LLM response."""
    r = llm_response
    if not r or not r.content or not r.content.parts: return r
    
    raw_text = r.content.parts[0].text or ""
    cleaned_sql = extract_sql_from_text(raw_text)
    
    r.content = types.Content(role="model", parts=[types.Part(text=cleaned_sql)])
    return r


def check_evaluation_success(callback_context: Any) -> Optional[types.Content]:
    """Check if query results are successful and terminate loop if data found.
    
    Returns:
        Content with termination message if data found, None otherwise
    """
    state = callback_context.session.state
    res = state.get("query_results", {})
    # DETERMINISTIC: If we have rows, exit the loop immediately. 
    if res.get("status") == "success" and res.get("rows"):
        callback_context._event_actions.escalate = True
        return types.Content(parts=[types.Part(text="Data found. Terminating loop.")])
    return None
