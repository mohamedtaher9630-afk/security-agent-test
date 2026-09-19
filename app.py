import sqlite3
from flask import Flask, request

app = Flask(__name__)

HARDCODED_API_KEY = "AIzaSyD-TEST-EXPOSED-KEY-998877665544"

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    cursor.execute(query)
    
    user = cursor.fetchone()
    if user:
        return "Welcome back!"
    return "Invalid credentials"

if __name__ == "__main__":
    app.run(debug=True)
