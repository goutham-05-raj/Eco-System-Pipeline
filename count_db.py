import sqlite3

c = sqlite3.connect('graphone.db')
print("Startups:", c.execute("SELECT COUNT(*) FROM startups").fetchone()[0])
print("Products:", c.execute("SELECT COUNT(*) FROM products").fetchone()[0])
print("Papers:", c.execute("SELECT COUNT(*) FROM research_papers").fetchone()[0])
