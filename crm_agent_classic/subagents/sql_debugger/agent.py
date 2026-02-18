"""SQL Debugger Agent - Fixes failing queries."""
import os
from google.adk.agents import Agent
from crm_agent.config import MODEL_NAME
from ..utils import clean_sql_output

# Load instruction from file
_instruction_path = os.path.join(os.path.dirname(__file__), "instruction.md")
with open(_instruction_path, "r") as f:
    _instruction = f.read()

sql_corrector_agent = Agent(
    model=MODEL_NAME, 
    name="sql_debugger", 
    description="Fixes SQL.", 
    instruction=_instruction, 
    output_key="sql_query", 
    after_model_callback=clean_sql_output
)
