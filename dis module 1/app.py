from flask import Flask, request, jsonify, render_template
from cryptography.fernet import Fernet

app = Flask(__name__)

# Generate a secure key (only for testing)
key = Fernet.generate_key()
cipher = Fernet(key)

@app.route('/')
def index():
    return render_template('index.html', key=key.decode())

@app.route('/encrypt', methods=['POST'])
def encrypt():
    data = request.json
    message = data.get('message', '').encode()
    key = data.get('key', '').encode()
    
    try:
        cipher = Fernet(key)
        encrypted_message = cipher.encrypt(message).decode()
        return jsonify({'result': encrypted_message})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/decrypt', methods=['POST'])
def decrypt():
    data = request.json
    message = data.get('message', '').encode()
    key = data.get('key', '').encode()

    try:
        cipher = Fernet(key)
        decrypted_message = cipher.decrypt(message).decode()
        return jsonify({'result': decrypted_message})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)  # ✅ Proper indentation
