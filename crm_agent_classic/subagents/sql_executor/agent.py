"""SQL Executor Agent - Executes SQL queries against the database."""
from google.adk.agents import BaseAgent
from google.adk.events import Event
from google.genai import types
from crm_agent.db import run_sql_query


class SqlExecutorAgent(BaseAgent):
    name: str = "sql_executor_agent"
    async def _run_async_impl(self, ctx):
        sql = ctx.session.state.get("sql_query")
        if not ctx.session.state.get("sql_valid", False):
            e = ctx.session.state.get("validation_error", "Validation failed.")
            ctx.session.state["query_results"] = {"status": "error", "error": e}
            yield Event(author=self.name, content=types.Content(parts=[types.Part(text=f"⚠️ Cannot Execute: Query failed validation.\n\nReason: {e}")]))
            return
        r = run_sql_query(sql)
        ctx.session.state["query_results"] = r
        
        if r.get("status") == "success":
            row_count = r.get("row_count", 0)
            msg = f"✓ Query Executed Successfully\n\nQuery: {sql}\n\nResults: {row_count} row(s) returned"
            if row_count > 0:
                msg += f"\nColumns: {', '.join(r.get('columns', []))}"
            yield Event(author=self.name, content=types.Content(parts=[types.Part(text=msg)]))
        else:
            yield Event(author=self.name, content=types.Content(parts=[types.Part(text=f"❌ Execution Error: {r.get('error', 'Unknown error')}\n\nQuery: {sql}")]))
