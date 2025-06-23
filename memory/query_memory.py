import sqlite3

conn = sqlite3.connect("memory/memory.db")
cursor = conn.cursor()

# Show all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("\n🔍 Tables in database:", tables)

# Explore the schema of the checkpoints table
# This is the core table where complete state snapshots are saved for each thread/session. When LangGraph reaches a checkpoint, it serializes the entire AgentState and stores it here.
cursor.execute("PRAGMA table_info(checkpoints);")
columns = cursor.fetchall()
print("\n📋  Schema of Table 'checkpoints':")
for col in columns:
    print(col)

# Explore the schema of the checkpoints table
cursor.execute("PRAGMA table_info(writes);")
columns = cursor.fetchall()
print("\n📋  Schema of Table 'writes':")
for col in columns:
    print(col)


# cursor.execute("SELECT DISTINCT thread_id FROM checkpoints")
# threads = cursor.fetchall()

# print("\n🧵 Saved Threads:")
# for thread in threads:
#     print("-", thread[0])

print("\n")

cursor.execute("SELECT checkpoint_id, parent_checkpoint_id, metadata type FROM checkpoints where thread_id = 'thread-20250530_230557_352'")
results = cursor.fetchall()
print("\n🧵 CHECK SPECIFIC Thread:")
for res in results:
    print("-", res)

print("\n")