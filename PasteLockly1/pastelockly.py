from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from Crypto.Cipher import AES
import base64
import os

app = Flask(__name__)

# Database setup
def init_db():
    with sqlite3.connect('database.db') as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS snippets
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         content TEXT NOT NULL,
                         is_encrypted INTEGER NOT NULL)''')

# Encrypt content using AES
def encrypt(content, secret_key):
    cipher = AES.new(secret_key, AES.MODE_EAX)
    nonce = cipher.nonce
    ciphertext, tag = cipher.encrypt_and_digest(content.encode())
    return base64.b64encode(nonce + ciphertext).decode('utf-8')

# Decrypt content using AES
def decrypt(encrypted_content, secret_key):
    try:
        data = base64.b64decode(encrypted_content)
        nonce, ciphertext = data[:16], data[16:]
        cipher = AES.new(secret_key, AES.MODE_EAX, nonce=nonce)
        return cipher.decrypt(ciphertext).decode('utf-8')
    except Exception:
        return None

@app.route('/')
def index():
    return render_template('create_snippet.html')  # Ensure this template exists

@app.route('/submit', methods=['POST'])
def submit():
    snippet = request.form['snippet']
    secret = request.form['secret']

    if secret:
        secret_key = secret.ljust(32)[:32].encode('utf-8')  # Padding/trimming key to 32 bytes
        encrypted_snippet = encrypt(snippet, secret_key)
        is_encrypted = 1
        content = encrypted_snippet
    else:
        is_encrypted = 0
        content = snippet

    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO snippets (content, is_encrypted) VALUES (?, ?)', (content, is_encrypted))
        conn.commit()
        snippet_id = cursor.lastrowid

    return redirect(url_for('view_snippet', snippet_id=snippet_id))

@app.route('/view/<int:snippet_id>')
def view_snippet(snippet_id):
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT content, is_encrypted FROM snippets WHERE id = ?', (snippet_id,))
        result = cursor.fetchone()

    if result is None:
        return "Snippet not found", 404

    content, is_encrypted = result
    if is_encrypted:
        return render_template('snippet_view.html', id=snippet_id, snippet=None)
    else:
        return render_template('snippet_view.html', snippet=content)

@app.route('/decrypt/<int:snippet_id>', methods=['POST'])
def decrypt_view(snippet_id):
    secret = request.form['secret']
    secret_key = secret.ljust(32)[:32].encode('utf-8')

    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT content FROM snippets WHERE id = ?', (snippet_id,))
        encrypted_content = cursor.fetchone()

    if encrypted_content is None:
        return "Snippet not found", 404

    decrypted_snippet = decrypt(encrypted_content[0], secret_key)
    if decrypted_snippet is None:
        return "Invalid secret key or decryption failed", 403

    return render_template('snippet_view.html', snippet=decrypted_snippet)

if __name__ == '__main__':
    init_db()  # Initialize the database if it doesn't exist
    app.run(debug=True)  # Enable debug mode for development
