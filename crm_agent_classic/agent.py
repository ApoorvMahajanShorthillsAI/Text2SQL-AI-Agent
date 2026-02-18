"""
CRM Agent Classic — Original multi-subagent pipeline.

Architecture:
  SequentialAgent (root)
    ├── SchemaExtractorAgent  → Loads DB schema into session state
    ├── rewrite_prompt_agent  → Rewrites user query into SQL requirements
    ├── sql_generator_agent   → Generates SQL from requirements
    ├── LoopAgent (sql_loop, max 3 iterations)
    │     ├── SqlValidatorAgent   → Validates SQL syntax
    │     ├── SqlExecutorAgent    → Executes SQL against DB
    │     ├── ResultVerifierAgent → Checks results, exits loop if data found
    │     └── sql_corrector_agent → Fixes SQL if validation/execution failed
    └── response_agent        → Formats final business answer

This agent is preserved for comparison against the Smart Planner agent.
"""

from google.adk.agents import SequentialAgent, LoopAgent
from .subagents import (
    rewrite_prompt_agent,
    sql_generator_agent,
    sql_corrector_agent,
    response_agent,
    SqlValidatorAgent,
    SchemaExtractorAgent,
    SqlExecutorAgent,
    ResultVerifierAgent,
)

# ── SQL Validation + Execution Loop ────────────────────────
sql_loop = LoopAgent(
    sub_agents=[
        SqlValidatorAgent(),
        SqlExecutorAgent(),
        ResultVerifierAgent(),
        sql_corrector_agent,
    ],
    max_iterations=3,
    name="sql_loop",
)

# ── Full Pipeline ───────────────────────────────────────────
root_agent = SequentialAgent(
    sub_agents=[
        SchemaExtractorAgent(),
        rewrite_prompt_agent,
        sql_generator_agent,
        sql_loop,
        response_agent,
    ],
    name="crm_agent_classic",
)
