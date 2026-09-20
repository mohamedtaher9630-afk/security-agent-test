from flask import Flask, request
import sqlite3

app = Flask(__name__)

@app.route('/login')
def login():
    username = request.args.get('user')
    # SQL Injection Vulnerability
    query = f"SELECT * FROM users WHERE username = '{username}'"
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute(query)
    return "Done"

if __name__ == '__main__':
    app.run()
