"""
CRM Agent — Powered by Gemini 2.5 Flash Thinking + BuiltInPlanner.

This agent uses Google's ADK LlmAgent with built-in planning capabilities.
Instead of a rigid multi-step pipeline, the model autonomously decides:
  1. When to inspect the schema
  2. How to construct SQL queries
  3. Whether to retry on failure
  4. How to present the final answer

Tools:
  - get_schema()    → Returns CREATE TABLE statements for all tables
  - run_sql_query() → Executes read-only SQL and returns results
"""

import os
from google.adk.agents.llm_agent import LlmAgent
from google.adk.planners import BuiltInPlanner
from google.genai.types import ThinkingConfig
from .config import MODEL_NAME
from .db import get_schema, run_sql_query

# ── Load Instructions ───────────────────────────────────────
_INSTRUCTION_PATH = os.path.join(os.path.dirname(__file__), "instruction.md")
with open(_INSTRUCTION_PATH, "r", encoding="utf-8") as f:
    _INSTRUCTION = f.read()

# ── Planner Configuration ──────────────────────────────────
_THINKING_BUDGET = 2048  # Max tokens for the model's internal reasoning

planner = BuiltInPlanner(
    thinking_config=ThinkingConfig(
        include_thoughts=True,
        thinking_budget=_THINKING_BUDGET,
    )
)

# ── Root Agent ──────────────────────────────────────────────
root_agent = LlmAgent(
    model=MODEL_NAME,
    name="crm_agent",
    description="A CRM Data Analyst that answers business questions by querying a SQLite database.",
    instruction=_INSTRUCTION,
    planner=planner,
    tools=[get_schema, run_sql_query],
)
