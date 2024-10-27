import sqlite3
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import os
import re

# Generate a random 32-byte AES key
def generate_key():
    key = os.urandom(32)  # 32 bytes for AES-256
    with open("aes_key.key", "wb") as key_file:
        key_file.write(key)
    return key

# Load the AES encryption key from a file
def load_key():
    return open("aes_key.key", "rb").read()

# Encrypt the master password using AES
def encrypt_password(password, key):
    iv = os.urandom(16)  # AES requires a 16-byte IV for CBC mode
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    # Padding the password to be a multiple of 16 bytes
    padder = padding.PKCS7(128).padder()
    padded_password = padder.update(password.encode()) + padder.finalize()

    encrypted_password = encryptor.update(padded_password) + encryptor.finalize()
    return iv + encrypted_password  # Store IV with the ciphertext

# Password validation
def password_validation(password):
    if (len(password) >= 17 and
        re.search(r'[A-Z]', password) and
        re.search(r'[a-z]', password) and
        re.search(r'[0-9]', password) and
        re.search(r'[!@#$%^&*(),.?":{}|<>]', password)):
        return True
    return False

# Set up the SQLite database
def setup_database(master_password):
    conn = sqlite3.connect('password_manager.db')
    c = conn.cursor()

    # Create table to store master password
    c.execute('''CREATE TABLE IF NOT EXISTS master_password (
                    id INTEGER PRIMARY KEY,
                    password BLOB
                )''')

    # Create table to store user accounts (encrypted passwords)
    c.execute('''CREATE TABLE IF NOT EXISTS accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    username TEXT NOT NULL,
                    password BLOB NOT NULL
                )''')

    # Insert encrypted master password
    key = load_key()
    encrypted_master_password = encrypt_password(master_password, key)
    c.execute("INSERT INTO master_password (password) VALUES (?)", (encrypted_master_password,))

    conn.commit()
    conn.close()

def main():
    key = generate_key()
    
    while True:
        master_password = input("Please set a master password (17 characters, upper/lowercase, numbers, special characters): ")
        if password_validation(master_password):
            setup_database(master_password)
            print("Database and master password setup successfully!")
            break
        else:
            print("Invalid password. Please meet the password criteria.")

if __name__ == "__main__":
    main()
