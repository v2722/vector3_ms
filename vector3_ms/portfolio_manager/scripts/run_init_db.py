import os
import re
from dotenv import load_dotenv
import mysql.connector

load_dotenv(os.path.join(os.path.dirname(__file__), os.pardir, ".env"))

HOST = os.getenv("DB_HOST", "localhost")
USER = os.getenv("DB_USER", "root")
PASS = os.getenv("DB_PASS", "")

path = os.path.join(os.path.dirname(__file__), "init_db.sql")
with open(path, "r", encoding="utf-8") as f:
    sql = f.read()

# Split on semicolons followed by a newline (Windows-safe: handles \r\n)
statements = re.split(r";\r?\n", sql)

conn = mysql.connector.connect(host=HOST, user=USER, password=PASS)
cursor = conn.cursor()
ran = 0
for stmt in statements:
    stmt = stmt.strip()
    if not stmt or stmt.startswith("--"):
        continue
    # strip leading/trailing comment-only lines
    lines = [ln for ln in stmt.splitlines() if not ln.strip().startswith("--")]
    clean = "\n".join(lines).strip()
    if not clean:
        continue
    try:
        cursor.execute(clean)
        ran += 1
    except mysql.connector.Error as e:
        print(f"[SKIP] {e.errno}: {e.msg}\n  -> {clean[:80]}")
conn.commit()
cursor.close()
conn.close()
print(f"Executed {ran} statements from init_db.sql")