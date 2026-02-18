"""Business Analyst Agent - Communicates insights."""
import os
from google.adk.agents import Agent
from crm_agent.config import MODEL_NAME

# Load instruction from file
_instruction_path = os.path.join(os.path.dirname(__file__), "instruction.md")
with open(_instruction_path, "r") as f:
    _instruction = f.read()

response_agent = Agent(
    model=MODEL_NAME, 
    name="business_analyst", 
    description="Communicates insights.", 
    instruction=_instruction, 
    output_key="final_answer"
)
