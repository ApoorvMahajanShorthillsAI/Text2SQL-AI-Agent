import difflib
import sqlite3
import os
from typing import Optional, List
from crm_agent.config.database import DB_PATH

def find_closest_entity(
    table_name: str, 
    column_name: str, 
    search_term: str, 
    cutoff: float = 0.6
) -> str:
    """
    Finds the closest matching value in a database column for a given search term using fuzzy matching.
    This is useful for correcting typos in entity names (e.g. 'Kancode' -> 'Kan-code').
    
    Args:
        table_name: The table to search (e.g., 'accounts_3').
        column_name: The column to search (e.g., 'account').
        search_term: The term to match (e.g., 'Kancode').
        cutoff: Minimum similarity score (0.0 to 1.0). Default 0.6.
        
    Returns:
        A string describing the best match found, or a message if no match is found.
    """
    if not table_name or not column_name or not search_term:
        return "Error: Missing table, column, or search term."
        
    # Security check: simple allow-list or basic validation to prevent injection if unchecked
    # But this is an internal tool used by the agent on a local DB.
    # We will trust the inputs for now but strip basics.
    clean_table = table_name.strip().replace(";", "").split()[0]
    clean_column = column_name.strip().replace(";", "").split()[0]
    
    sql = f"SELECT DISTINCT {clean_column} FROM {clean_table} WHERE {clean_column} IS NOT NULL"
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        conn.close()
        
        # Flatten list of tuples to list of strings
        candidates = [str(row[0]) for row in rows if row[0]]
        
        # Use difflib to find matching candidates
        # n=3 to see top 3 if needed, but we'll return top 1 for simplicity of the agent
        matches = difflib.get_close_matches(search_term, candidates, n=1, cutoff=cutoff)
        
        if matches:
            best_match = matches[0]
            # Calculate a quick confidence? difflib doesn't give score directly in this function.
            # But if it passed cutoff, it's good.
            return f"Found fuzzy match: '{best_match}' (Original search: '{search_term}')"
        else:
            return f"No fuzzy match found for '{search_term}' in {clean_table}.{clean_column} (Checked {len(candidates)} values)"
            
    except Exception as e:
        return f"Database Error during fuzzy search: {str(e)}"
