"""Schema Extractor Agent - Extracts and caches database schema."""
from google.adk.agents import BaseAgent
from google.adk.events import Event
from google.genai import types
from crm_agent.db import get_schema


class SchemaExtractorAgent(BaseAgent):
    name: str = "schema_extractor_agent"
    async def _run_async_impl(self, ctx):
        s = get_schema()
        ctx.session.state["db_schema"] = s
        table_count = s.count("CREATE TABLE")
        yield Event(author=self.name, content=types.Content(parts=[types.Part(text=f"✓ Database Schema Loaded: Extracted schema for {table_count} table(s) from CRM database.\n\n{s}")]))
