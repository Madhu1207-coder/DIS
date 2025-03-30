from flask import Flask, render_template, request, send_file, redirect, url_for
from Crypto.Cipher import DES
from Crypto.Util.Padding import pad, unpad
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
ENCRYPTED_FOLDER = "encrypted"
DECRYPTED_FOLDER = "decrypted"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(ENCRYPTED_FOLDER, exist_ok=True)
os.makedirs(DECRYPTED_FOLDER, exist_ok=True)

def generate_key():
    return os.urandom(8)

def encrypt_file(file_path, key):
    cipher = DES.new(key, DES.MODE_CBC)
    with open(file_path, 'rb') as f:
        plaintext = f.read()
    padded_text = pad(plaintext, DES.block_size)
    ciphertext = cipher.encrypt(padded_text)
    encrypted_filename = os.path.basename(file_path) + ".enc"
    encrypted_file_path = os.path.join(ENCRYPTED_FOLDER, encrypted_filename)
    with open(encrypted_file_path, 'wb') as f:
        f.write(cipher.iv + ciphertext)
    return encrypted_filename

def decrypt_file(filename, key):
    encrypted_file_path = os.path.join(ENCRYPTED_FOLDER, filename)
    if not os.path.exists(encrypted_file_path):
        return None
    with open(encrypted_file_path, 'rb') as f:
        iv = f.read(8)
        ciphertext = f.read()
    cipher = DES.new(key, DES.MODE_CBC, iv)
    plaintext = unpad(cipher.decrypt(ciphertext), DES.block_size)
    decrypted_filename = filename.replace(".enc", "")
    decrypted_file_path = os.path.join(DECRYPTED_FOLDER, decrypted_filename)
    with open(decrypted_file_path, 'wb') as f:
        f.write(plaintext)
    return decrypted_filename

'''@app.route('/decrypt', methods=['POST'])
def decrypt():
    if 'filename' not in request.form or 'key' not in request.form:
        return "Error: Missing filename or key", 400  # Handle missing fields properly

    filename = request.form['filename']
    key_hex = request.form['key']
    
    try:
        key = bytes.fromhex(key_hex)
    except ValueError:
        return "Error: Invalid key format", 400  # Handle invalid key formats

    decrypted_filename = decrypt_file(filename, key)
    if decrypted_filename:
        return render_template('decrypt.html', decrypted_file=decrypted_filename, filename=filename)
    else:
        return "Error: File not found or incorrect key", 404'''
        

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)
    return render_template('options.html', filename=file.filename)

@app.route('/encrypt/<filename>')
def encrypt(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    key = generate_key()
    encrypted_filename = encrypt_file(file_path, key)
    return render_template('encrypt.html', key=key.hex(), encrypted_file=encrypted_filename)

@app.route('/decrypt_page/<filename>')
def decrypt_page(filename):
    return render_template('decrypt.html', filename=filename)

@app.route('/decrypt', methods=['POST'])
def decrypt():
    filename = request.form.get('filename')
    key_hex = request.form.get('key')

    if not filename or not key_hex:
        return render_template('decrypt.html', filename=filename, error="Error: Missing filename or key")

    try:
        key = bytes.fromhex(key_hex)  # Convert hex input to bytes
        if len(key) != 8:  # DES key must be 8 bytes (16 hex digits)
            raise ValueError("Invalid key length")
    except ValueError:
        return render_template('decrypt.html', filename=filename, error="Error: Invalid key format. Enter 16 hex digits.")

    decrypted_filename = decrypt_file(filename, key)

    if decrypted_filename:
        return render_template('decrypt.html', decrypted_file=decrypted_filename, filename=filename)
    else:
        return render_template('decrypt.html', filename=filename, error="Error: File not found or incorrect key")

@app.route('/download/<path:filename>')
def download(filename):
    file_path = os.path.join(ENCRYPTED_FOLDER, filename) if filename.endswith(".enc") else os.path.join(DECRYPTED_FOLDER, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return "Error: File not found", 404

if __name__ == '__main__':
    app.run(debug=True,use_reloader = False)
