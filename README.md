# CRM Agent (Hybrid Architecture v2.0)

An autonomous Data Analyst Agent that answers complex business questions by querying a fragmented SQLite database. 

## 🚀 Key Features

- **Hybrid Architecture**: Combines a deterministic **Sequential Chain** with a reasoning **Planner Agent**.
  - *Reliability*: Strict process flow (Context → Code → Data → Answer).
  - *Intelligence*: Uses `PlanReActPlanner` to dynamically reason about table joins and aggregation logic.
- **Self-Healing SQL**: A dedicated loop validates, executes, and automatically corrects SQL errors using error feedback.
- **Fragmented Data Handling**: Capable of joining data across disconnected tables (e.g. Sales Pipeline + 10 separate Monthly Order tables).

## 🛠️ Architecture

The system uses `google-adk` to orchestrate a pipeline of specialized agents:

1.  **Schema Extractor**: Loads database context.
2.  **Query Analyst**: Clarifies user intent.
3.  **Smart SQL Architect**: Uses LLM planning to generate reasoned SQL.
4.  **SQL Loop**: Validator → Executor → Verifier → Corrector.
5.  **Business Analyst**: Formats the final natural language response.

## 📦 Setup & Usage

1.  **Prerequisites**:
    - Python 3.10+
    - Google Cloud Project with Vertex AI API enabled.
    - `GOOGLE_API_KEY` set in your environment.

2.  **Install Dependencies**:
    ```bash
    pip install google-adk google-genai
    ```

3.  **Run the Agent**:
    ```bash
    adk web
    ```
    Then open http://localhost:8080 and select `crm_agent_classic` (The Hybrid Agent).

## 🧪 Example Queries

- *"What is the total revenue from Won deals?"*
- *"Show top 3 accounts by revenue and their sales team."*
- *"Monthly revenue trend for 2017."*
