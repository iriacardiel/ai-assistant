import sqlite3

db_path = "memory/memory.db"  # Update if your DB is in a different path
conn = sqlite3.connect(db_path)

# Wipe all session data
conn.execute("DELETE FROM checkpoints")
conn.execute("DELETE FROM writes")
conn.commit()

print("✅ All LangGraph session data has been deleted from memory.db.")
