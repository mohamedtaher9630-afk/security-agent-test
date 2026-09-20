from flask import Flask, request
import sqlite3

app = Flask(__name__)

@app.route('/login')
def login():
    username = request.args.get('user')
    # Parameterized query prevents SQL Injection
    query = "SELECT * FROM users WHERE username = ?"
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute(query, (username,))
    rows = cursor.fetchall()
    conn.close()
    return "Done"

if __name__ == '__main__':
    app.run()