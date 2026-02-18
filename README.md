# CRM SQL Agent

A sophisticated multi-agent system that converts natural language questions into SQL queries and executes them against a CRM database, using Google's Gemini 2.0 Flash model and the ADK (Agent Development Kit) framework.

## Overview

This intelligent agent system analyzes business questions about your CRM data, generates optimized SQL queries with fuzzy matching for robust data retrieval, and returns professional business insights.

**Key Features:**
- 🎯 **Role-Based Architecture**: Specialized agents for query analysis, SQL generation, validation, execution, and response formatting
- 🔍 **Fuzzy Matching**: Handles typos and variations in data (e.g., "Software" vs "technolgy")
- 🔄 **Self-Correcting Loop**: Automatically refines queries if no results found
- ✅ **SQL Validation**: Syntax checking with sqlglot before execution
- 🛡️ **Safety**: Blocks destructive operations (INSERT, UPDATE, DELETE, etc.)

---

## Architecture

The agent follows a **Sequential → Loop → Response** workflow:

```
┌─────────────────────────────────────────────────────────┐
│                   SequentialAgent                        │
│                                                          │
│  1. SchemaExtractor → Retrieves database schema          │
│  2. QueryAnalyst    → Refines NL to SQL requirements     │
│  3. SQLArchitect    → Generates SQL with fuzzy matching  │
│  4. ┌────────────── LoopAgent ──────────────┐           │
│     │  a. SQLValidator   → Syntax check      │           │
│     │  b. SQLExecutor    → Run query         │           │
│     │  c. ResultVerifier → Check for data    │           │
│     │  d. SQLDebugger    → Broaden filters   │           │
│     └──────────────────────────────────────┘           │
│  5. BusinessAnalyst → Format professional answer         │
└─────────────────────────────────────────────────────────┘
```

### Agent Roles

| Agent | Role | Responsibility |
|-------|------|---------------|
| **Schema Extractor** | Infrastructure | Caches database schema for reference |
| **Query Analyst** | Business Analysis | Maps business terms to SQL requirements |
| **SQL Architect** | Database Engineering | Generates high-performance queries with fuzzy logic |
| **SQL Validator** | Quality Assurance | Validates syntax before execution |
| **SQL Executor** | Operations | Executes queries safely against database |
| **Result Verifier** | Quality Control | Checks if data was found |
| **SQL Debugger** | Problem Solving | Broadens filters when no results found |
| **Business Analyst** | Communication | Formats insights for stakeholders |

---

## Project Structure

```
crm_agent_project/
├── crm_agent/                  # Main agent package (ADK entry point)
│   ├── __init__.py             # Exports root_agent
│   ├── agent.py                # Agent orchestration
│   ├── db.py                   # Database helpers (typed)
│   ├── .env                    # API keys
│   ├── .adk/                   # Session storage
│   │   └── session.db
│   ├── config/                 # Configuration module
│   │   ├── __init__.py
│   │   ├── model.py            # MODEL_NAME
│   │   └── database.py         # DB_PATH
│   └── subagents/              # Individual agent modules
│       ├── __init__.py         # Exports all subagents
│       ├── utils.py            # Shared callbacks (typed)
│       ├── query_analyst/      # Refines requirements
│       │   ├── agent.py
│       │   ├── instruction.md
│       │   └── __init__.py
│       ├── sql_architect/      # Generates SQL
│       ├── sql_debugger/       # Fixes queries
│       ├── business_analyst/   # Formats responses
│       ├── sql_validator/      # Validates syntax
│       ├── schema_extractor/   # Extracts schema
│       ├── sql_executor/       # Runs queries
│       └── result_verifier/    # Checks results
├── data/                       # Database & raw CSV files
│   ├── __init__.py             # CSV → SQLite import
│   ├── crm.db                  # SQLite database
│   └── *.csv                   # Raw data files
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <your-repo>
cd crm_agent_project

# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\Activate.ps1   # Windows PowerShell
source .venv/bin/activate     # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create `.env` file in `crm_agent/` directory:
```env
GOOGLE_API_KEY=your_api_key_here
```

### 3. Run the Agent

```bash
# Start ADK web interface
adk web

# Select "crm_agent" from the dropdown
# Open http://localhost:8000 in your browser
```

### 4. Example Queries

Try asking:
- "Which manager's team generated the highest revenue from Software deals in 2017?"
- "Show me all accounts in the Medical sector"
- "What's the total value of Won deals this year?"

---

## Development

### Modifying Agent Instructions

Each agent's behavior is controlled by an `instruction.md` file in its directory:

```bash
crm_agent/subagents/sql_architect/instruction.md
```

Edit these files to customize:
- Agent identity and role
- Decision-making guidelines
- Few-shot examples
- Output formatting rules

Changes take effect on next agent reload (restart `adk web`).

### Database Schema

The CRM database includes:
- **accounts** - Company information, sectors, and office locations
- **products** - Product catalog with pricing
- **sales_teams** - Sales agents, managers, and status (Current/Left)
- **sales_pipeline** - Deals, stages, close values, and historical orders

To rebuild the database:
```bash
python -m data
```

### Adding New Agents

1. Create agent directory in `subagents/`
2. Add `agent.py` with agent definition
3. Add `instruction.md` with agent prompt
4. Add `__init__.py` to export agent
5. Update `subagents/__init__.py` to include new agent
6. Import in `agent.py` orchestration

---

## Type Safety

The codebase uses comprehensive type hints for IDE support:

```python
def run_sql_query(sql: str) -> Dict[str, Any]:
    """Execute a read-only SQL query."""
    ...
```

All major functions in `db.py` and `subagents/utils.py` are fully typed.

---

## Security

- ✅ **Read-only queries**: Blocks INSERT, UPDATE, DELETE, DROP, etc.
- ✅ **Syntax validation**: Uses sqlglot to catch errors before execution
- ✅ **Safe fuzzy matching**: Uses LIKE patterns instead of exact matches
- ✅ **API key protection**: Stored in `.env` (not committed to git)

---

## License

MIT License - See LICENSE file for details

---

## Troubleshooting

**Q: Red wavy lines in VS Code imports?**  
A: Disable the Pyre2 extension or ensure your Python interpreter points to `.venv/Scripts/python.exe`

**Q: Agent not finding data?**  
A: Check the fuzzy matching patterns in `instruction.md` files - the agent uses `LIKE '%term%'` to handle typos

**Q: Database connection errors?**  
A: Verify `data/crm.db` exists by running `python -m data` to rebuild from CSVs

---

*Built with ❤️ using Google Gemini 2.0 and ADK*
