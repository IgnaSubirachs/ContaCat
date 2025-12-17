#!/usr/bin/env python
import mysql.connector
from passlib.context import CryptContext

# Create password context
pwd_context = CryptContext(schemes=["pbkdf2_sha256", "bcrypt"], deprecated="auto")

# Hash the password
password_hash = pwd_context.hash("admin123")

# Connect to database
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="erpdb"
)

cursor = conn.cursor()

# Update admin password
cursor.execute("UPDATE users SET password_hash = %s WHERE username = 'admin'", (password_hash,))
conn.commit()

print(f"Password updated successfully for admin")
print(f"New hash: {password_hash}")

cursor.close()
conn.close()
