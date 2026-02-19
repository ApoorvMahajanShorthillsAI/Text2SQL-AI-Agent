"""SQL Architect Agent - Generates SQLite queries using PlanReActPlanner."""
import os
from typing import Any
from google.adk.agents.llm_agent import LlmAgent
from google.adk.planners import PlanReActPlanner
from crm_agent.config import MODEL_NAME
from crm_agent.db import run_sql_query
from ..utils import extract_sql_from_text
from crm_agent_classic.subagents.tools import find_closest_entity

# Load instruction from file
_instruction_path = os.path.join(os.path.dirname(__file__), "instruction.md")
with open(_instruction_path, "r") as f:
    _INSTRUCTION = f.read()

# Append critical formatting instruction
_INSTRUCTION += "\n\nCRITICAL: Your final answer MUST be the final SQL query only. Do not wrap it in markdown blocks. Do not explain. Just the raw SQL string."

class SmartSqlArchitectAgent(LlmAgent):
    """Custom LlmAgent that saves its final answer (SQL) to session state."""
    
    async def _run_async_impl(self, ctx):
        # Run the standard LlmAgent logic (Plan -> React loop)
        # We iterate over the event stream yielded by the planner
        async for event in super()._run_async_impl(ctx):
            # If the event has content (the final answer), capture it
            if event.content and event.content.parts:
                final_sql = event.content.parts[-1].text or ""
                
                # Clean and save to session state for the downstream loop
                cleaned_sql = extract_sql_from_text(final_sql)
                ctx.session.state["sql_query"] = cleaned_sql
            
            # Yield the event so the pipeline continues
            yield event

# Instantiate the agent
sql_generator_agent = SmartSqlArchitectAgent(
    model=MODEL_NAME,
    name="sql_architect",
    description="Generates high-performance SQLite queries using explicit planning.",
    instruction=_INSTRUCTION,
    planner=PlanReActPlanner(),
    tools=[run_sql_query, find_closest_entity],  # Added robust fuzzy tool
)
