import sqlite3

conn = sqlite3.connect("chat.db", check_same_thread=False)
cursor = conn.cursor()

def init_db():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_msg TEXT,
        bot_msg TEXT
    )
    """)
    conn.commit()

def save_chat(user, bot):
    cursor.execute(
        "INSERT INTO chats (user_msg, bot_msg) VALUES (?, ?)",
        (user, bot)
    )
    conn.commit()

def get_memory(limit=5):
    cursor.execute(
        "SELECT user_msg, bot_msg FROM chats ORDER BY id DESC LIMIT ?",
        (limit,)
    )
    rows = cursor.fetchall()[::-1]

    messages = []
    for u, b in rows:
        messages.append({"role": "user", "content": u})
        messages.append({"role": "assistant", "content": b})

    return messages
