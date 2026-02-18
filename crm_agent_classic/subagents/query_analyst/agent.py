"""Query Analyst Agent - Refines NL questions into SQL requirements."""
import os
from google.adk.agents import Agent
from crm_agent.config import MODEL_NAME

# Load instruction from file
_instruction_path = os.path.join(os.path.dirname(__file__), "instruction.md")
with open(_instruction_path, "r") as f:
    _instruction = f.read()

rewrite_prompt_agent = Agent(
    model=MODEL_NAME, 
    name="query_analyst", 
    description="Refines requirements.", 
    instruction=_instruction, 
    output_key="rewritten_query"
)
