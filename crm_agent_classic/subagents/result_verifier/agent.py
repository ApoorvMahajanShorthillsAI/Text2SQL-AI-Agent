"""Result Verifier Agent - Verifies query results and controls loop termination."""
from google.adk.agents import BaseAgent
from google.adk.events import Event, EventActions
from google.genai import types


class ResultVerifierAgent(BaseAgent):
    name: str = "result_verifier_agent"
    async def _run_async_impl(self, ctx):
        res = ctx.session.state.get("query_results", {})
        
        # Check for explicit error result from Architect (e.g. SELECT 'Error: ...')
        rows = res.get("rows", [])
        if rows and len(rows) == 1 and str(rows[0][0]).lower().startswith("error"):
            # It's a verified failure (Architect correctly identified data is missing)
            error_msg = rows[0][0]
            yield Event(
                author=self.name, 
                content=types.Content(parts=[types.Part(text=f"✓ Verified Handling: {error_msg}. Passing to response agent.")]),
                actions=EventActions(escalate=True)
            )
        elif res.get("status") == "success" and rows:
            row_count = res.get("row_count", len(rows))
            yield Event(
                author=self.name, 
                content=types.Content(parts=[types.Part(text=f"✓ Success: Found {row_count} matching record(s). Terminating refinement loop and proceeding to response generation.")]),
                actions=EventActions(escalate=True)
            )
        else:
            reason = "Query returned no results" if res.get("status") == "success" else f"Error: {res.get('error', 'Unknown')}"
            iteration = ctx.session.state.get("_loop_iteration", 0) + 1
            yield Event(author=self.name, content=types.Content(parts=[types.Part(text=f"⟳ Attempt {iteration}: {reason}. Broadening search filters and retrying...")]))
