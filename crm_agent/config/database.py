"""Database configuration."""
import os
from dotenv import load_dotenv

# Load environment variables from parent directory (.env is in crm_agent/)
_config_dir = os.path.dirname(__file__)
_crm_agent_dir = os.path.dirname(_config_dir)
load_dotenv(os.path.join(_crm_agent_dir, ".env"))

# Project root is two levels up from config directory
PROJECT_ROOT: str = os.path.dirname(_crm_agent_dir)
DB_PATH: str = os.path.join(PROJECT_ROOT, "data", "crm.db")
