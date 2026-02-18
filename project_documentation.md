# CRM Data Analyst Agent - Technical Documentation
> **Version**: 2.0 (Hybrid Architecture)
> **Status**: Production-Ready / Verified
> **Date**: February 18, 2026

## 1. Project Overview
The **CRM Data Analyst Agent** is an autonomous AI system designed to answer complex business questions by querying a fragmented SQLite database. Unlike traditional text-to-SQL tools that struggle with ambiguous schemas and multi-step reasoning, this agent employs a **Hybrid Architecture** that combines the reliability of a deterministic pipeline with the reasoning capabilities of a Large Language Model (LLM).

**Core Capabilities:**
- **Complex Reasoning**: Can deduce relationships between disconnected tables (e.g., aggregating monthly orders vs. pipeline deals).
- **Self-Correction**: detects and fixes SQL errors automatically.
- **Ambiguity Resolution**: Clarifies user intent before generating code.
- **Business Logic Enforcement**: Strictly adheres to business rules (e.g., "Won deals come from `sales_pipeline`, not monthly tables").

---

## 2. Architectural Evolution

The system evolved through three distinct phases to address specific challenges in reliability and accuracy.

### Phase 1: Classic Pipeline (`crm_agent_classic`)
*The "Assembly Line" Approach.*
- **Design**: A rigid `SequentialAgent` pipeline of 8 specialized subagents (Schema → Rewrite → SQL Gen → Validate → Execute → Verify → Respond).
- **Strength**: High control and predictability.
- **Weakness**: The `sql_architect` was a "dumb" text generator. It often failed on complex queries because it couldn't "think" about schema relationships or test its own SQL before execution.

### Phase 2: Smart Agent (`crm_agent`)
*The "Monolithic Brain" Approach.*
- **Design**: A single `LlmAgent` offering `gemini-2.5-flash` with a `BuiltInPlanner`.
- **Strength**: Highly autonomous; could reason through problems dynamically.
- **Weakness**: Prone to **hallucination**. Without the strict guardrails of the pipeline, it would sometimes invent columns or ignore business rules.

### Phase 3: Hybrid Agent (Current System)
*The "Best of Both Worlds" Approach.*
- **Design**: We retained the robust **Phase 1 Pipeline** but surgically replaced the weak `sql_architect` with a **Phase 2-style Planner Agent**.
- **Result**: The agent now follows a strict process (Pipeline) but calculates the SQL using advanced reasoning (Planner), resulting in high accuracy and reliability.

---

## 3. High-Level Architecture (Current System)

The system uses a **Sequential Pipeline** architecture where data flows through a series of specialized agents.

**Major Components:**
1.  **Orchestrator (`SequentialAgent`)**: Manages the end-to-end flow.
2.  **Specialist Subagents**:
    *   **Schema Extractor**: Loads database structure context.
    *   **Query Analyst**: Translates vague questions into technical requirements.
    *   **Smart SQL Architect (Hybrid)**: The core intelligence. Reasons about data and generates verified SQL.
    *   **SQL Loop**: A self-healing execution loop (Validator → Executor → Verifier → Corrector).
    *   **Business Analyst**: Formats the final answer for the user.

---

## 4. Architecture Diagram

```mermaid
graph TD
    UserQuery[User Query] --> Orchestrator{SequentialAgent Orchestrator}
    
    subgraph "Preparation Phase"
        Orchestrator --> Schema[Schema Extractor]
        Schema --> QueryAnalyst[Query Analyst]
        QueryAnalyst --> RewrittenPrompt[Rewritten Prompt]
    end
    
    subgraph "Intelligence Phase (Hybrid Core)"
        RewrittenPrompt --> SmartSQL[Smart SQL Architect\n(LlmAgent + PlanReActPlanner)]
        SmartSQL -- "Reasoning & Testing" --> SQL[Generated SQL]
    end
    
    subgraph "Execution Phase (Self-Healing Loop)"
        SQL --> Validator[SQL Validator]
        Validator -- "Valid?" --> Executor[SQL Executor]
        Executor -- "Success?" --> Verifier[Result Verifier]
        Verifier -- "Data Found?" --> Output
        
        Validator -- "Invalid" --> Corrector[SQL Corrector]
        Executor -- "Error" --> Corrector
        Corrector -- "Fix" --> Validator
    end
    
    Output[Final Result Data] --> BusinessAnalyst[Business Analyst]
    BusinessAnalyst --> FinalResponse[Final Response]
```

---

## 5. Technology Stack

| Component | Technology | Reasoning |
| :--- | :--- | :--- |
| **Framework** | `google-adk` (Agent Development Kit) | Provides robust `SequentialAgent` and `LlmAgent` abstractions. |
| **Model** | `gemini-2.5-flash` | Selected for high reasoning capability ("thinking" mode) and low latency. |
| **Planner** | `PlanReActPlanner` | Enables the SQL Architect to think step-by-step ("Plan-Reason-Act") before acting. |
| **Database** | SQLite | Lightweight, distinct file-based structure ideal for testing fragmented schemas. |
| **Parsing** | `sqlglot` | Used for syntax validation and transpilation. |

---

## 6. System Workflow (Detailed)

1.  **Schema Extractor**: Connects to the DB, extracts `CREATE TABLE` statements, and injects them into the session context.
2.  **Query Analyst**: Analyzes the user's natural language request. It clarifies ambiguities (e.g., "top accounts" -> "top accounts by revenue") and sets the strategy.
3.  **Smart SQL Architect**:
    *    Receives the requirement.
    *   **Plans**: Decides which tables are needed (`sales_pipeline` vs `monthly_orders`).
    *   **Reasons**: Determines join logic (e.g., handling one-to-many relationships).
    *   **Tests**: Can internally run `run_sql_query` to verify assumptions.
    *   **Outputs**: Produces a high-confidence SQL query.
4.  **SQL Loop**:
    *   **Validator**: Statistically checks SQL syntax.
    *   **Executor**: Runs the query against the production DB (Read-Only).
    *   **Verifier**: checks if rows were returned.
    *   **Corrector**: If any step fails, this agent (LLM) analyzes the error and regenerates the SQL.
5.  **Business Analyst**: Takes the raw JSON result and the original question to formulate a human-readable text response.

---

## 7. Database Design & Reasoning Challenges

The database is intentionally designed to be **fragmented** to test the agent's logical capabilities.

**Key Challenges:**
*   **Duplicate Data Sources**: Revenue exists in both `sales_pipeline` (deal-based) and 10 separate `monthly_order` tables (order-based).
    *   *Golden Rule*: "Use `sales_pipeline` for deal stages (Won/Lost). Use monthly tables for time-series analysis. NEVER join them."
*   **Split Account Info**: Basic info is in `accounts_3`, but location data is in `intl_accounts`.
*   **Structure Mismatches**: International accounts have `office_location`, domestic ones do not (implying 'N/A').

**Strategy**: The **Smart SQL Architect** is explicitly instructed on these rules and uses its reasoning planner to select the correct path purely based on the question context.

---

## 8. Key Design Decisions

### **Hybrid Architecture (Sequential + Planner)**
We chose to embed an `LlmAgent` (Planner) inside a `SequentialAgent` (Pipeline).
*   *Why?* A purely sequential pipeline is too rigid for complex SQL generation. A purely autonomous agent is too unpredictable. The hybrid approach gives us **structured control flow** with **intelligent execution steps**.

### **PlanReActPlanner**
We switched the `sql_architect` to use `PlanReActPlanner`.
*   *Why?* The reasoning trace (Plan -> Thought -> Act) allows us to debug *why* the agent chose a specific table or join. It also allows the agent to self-correct ("Wait, I shouldn't join these tables") *before* generating the final SQL.

### **The "SQL Loop" Pattern**
We implemented a dedicated feedback loop for SQL execution.
*   *Why?* SQL generation is prone to minor syntax errors. Instead of failing the whole request, the loop allows a specialized "Corrector" agent to fix the SQL based on the specific error message (e.g., "no such column") and retry immediately.

---

## 9. Representative Code Snippets

### A. The Hybrid Pipeline (`crm_agent_classic/agent.py`)
orchestrates the flow, treating the smart agent (`sql_generator_agent`) as just another step.

```python
# The Hybrid Pipeline
root_agent = SequentialAgent(
    sub_agents=[
        SchemaExtractorAgent(),     # 1. Load context
        rewrite_prompt_agent,       # 2. Clarify intent
        sql_generator_agent,        # 3. Smart SQL Generation (Hybrid Step)
        sql_loop,                   # 4. Execution & Correction Loop
        response_agent,             # 5. Final Answer
    ],
    name="crm_agent_classic",
)
```

### B. The Smart SQL Architect (`sql_architect/agent.py`)
This is the "Brain" of the hybrid system. It captures the verified SQL output.

```python
class SmartSqlArchitectAgent(LlmAgent):
    """Custom LlmAgent using PlanReAct to reason about SQL."""
    
    async def _run_async_impl(self, ctx):
        # Intercept the planner's event stream
        async for event in super()._run_async_impl(ctx):
            if event.content and event.content.parts:
                # Capture the final, reasoned SQL
                final_sql = event.content.parts[-1].text
                # Save to session for the downstream pipeline
                ctx.session.state["sql_query"] = extract_sql_from_text(final_sql)
            yield event

sql_generator_agent = SmartSqlArchitectAgent(
    model=MODEL_NAME,
    planner=PlanReActPlanner(),     # <--- The Reasoning Engine
    tools=[run_sql_query],          # <--- Capability to test SQL
    instruction=...
)
```

---

## 10. Reliability & Debugging Strategy

**Why is this stable?**
1.  **Deterministic Flow**: The high-level steps (Context -> Code -> Data -> Answer) never change.
2.  **Reasoned SQL**: The SQL step is no longer a guess; it's a planned output derived from schema analysis.
3.  **Self-Correction**: The `SQL Loop` acts as a safety net. If the Smart Architect *does* make a mistake, the Corrector catches it.

**Verified Success Scenario:**
*   *Query*: "Top 3 accounts by revenue with sales team."
*   *Complexity*: Requires joining aggregated revenue data with multi-value text fields (sales teams).
*   *Outcome*: The agent correctly identified the need for `sales_pipeline` (revenue), `sales_teams_1` (teams), and `intl_accounts` (location), and acted to `GROUP_CONCAT` the one-to-many team relationship.

---

## 11. Limitations & Future Improvements

*   **Latency**: The `PlanReActPlanner` adds times (reasoning iterations) compared to a zero-shot generator.
    *   *Improvement*: Implement caching for common queries or schema analysis results.
*   **Token Usage**: The "Thinking" process consumes more tokens per request.
*   **Database Scope**: Currently limited to Read-Only operations.
    *   *Improvement*: Add controlled Write capabilities (e.g., "Update customer status") with strict approval gates.
