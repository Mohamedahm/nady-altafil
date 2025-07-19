import sqlite3

conn = sqlite3.connect("database.db")
c = conn.cursor()

c.execute("SELECT * FROM subscribers")
rows = c.fetchall()

print("المشتركين:\n")
for row in rows:
    print(f"ID: {row[0]}, Name: {row[1]}, Email: {row[2]}, Start Date: {row[3]}, Paid: {row[4]}, Payment Email Sent: {row[5]}")

conn.close()


import sqlite3

conn = sqlite3.connect("database.db")
c = conn.cursor()

c.execute("SELECT * FROM subscribers")
rows = c.fetchall()

print("المشتركين:\n")
for row in rows:
    print(f"🧾 الصف الكامل: {row}")  # نطبع كل الصف كما هو

conn.close()
