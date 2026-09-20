# Security Audit Test

from flask import Flask, request, render_template_string
import sqlite3

app = Flask(__name__)
hardcoded_password = "12345"
@app.route('/')
def index():
    user_input = request.args.get('name', 'Guest')
    # Vulnerable SQL query for testing AI Security Agent
    query = f"SELECT * FROM users WHERE name = '{user_input}'"
    return render_template_string(f"<h1>Welcome, {user_input}!</h1>")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
