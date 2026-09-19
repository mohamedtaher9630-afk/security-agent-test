import sqlite3
import os
from flask import Flask, request

app = Flask(__name__)

# Retrieve API key securely from environment variables
API_KEY = os.getenv("API_KEY")

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    
    # Parameterized query to prevent SQL Injection
    query = "SELECT * FROM users WHERE username = ? AND password = ?"
    cursor.execute(query, (username, password))
    
    user = cursor.fetchone()
    conn.close()
    if user:
        return "Welcome back!"
    return "Invalid credentials"

if __name__ == "__main__":
    app.run(debug=False)