import sqlite3
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import os
import re

# Load the AES encryption key from a file
def load_key():
    return open("aes_key.key", "rb").read()

# Encrypt the password using AES
def encrypt_password(password, key):
    iv = os.urandom(16)  # AES requires a 16-byte IV for CBC mode
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    # Padding the password to be a multiple of 16 bytes
    padder = padding.PKCS7(128).padder()
    padded_password = padder.update(password.encode()) + padder.finalize()

    encrypted_password = encryptor.update(padded_password) + encryptor.finalize()
    return iv + encrypted_password  # Store IV with the ciphertext

# Decrypt the password using AES
def decrypt_password(encrypted_password, key):
    print(f"Encrypted Password Length: {len(encrypted_password)}")
    iv = encrypted_password[:16]  # First 16 bytes are the IV
    encrypted_password = encrypted_password[16:]  # Remaining bytes are the ciphertext

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    padded_password = decryptor.update(encrypted_password) + decryptor.finalize()

    # Remove padding
    unpadder = padding.PKCS7(128).unpadder()
    password = unpadder.update(padded_password) + unpadder.finalize()

    return password.decode()

# Validate input (master password)
def input_validation(user_input):
    return bool(re.match(r'[A-Za-z0-9!@#$%^&*(),.?":{}|<>]{17,}', user_input))

def sql_injection_check(user_input):

    #Returns false if there is potential for SQL Injection based on these patterns
    #THIS WAS GGENERATED BY GPT4
    sql_injection_patterns = [
            r"'.*--",            # Commenting out the rest of the query
            r"'.*;",             # Termination of statement
            r"SELECT.*FROM",     # SELECT statement
            r"INSERT.*INTO",     # INSERT statement
            r"UPDATE.*SET",      # UPDATE statement
            r"DELETE.*FROM",     # DELETE statement
            r"\bUNION\b",        # UNION keyword
            r"\bOR\b",           # OR keyword
            r"\bAND\b",          # AND keyword
            r"EXEC",             # EXEC command
        ]
    #THIS IS THE END OF THE GENERATED CODE

    for i in sql_injection_patterns:
        if re.search(i, user_input, re.IGNORECASE):
            return False
    return True
# Connect to the database
def connect_db():
    try:
        conn = sqlite3.connect('password_manager.db')
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None

# Verify the master password
def verify_master_password(input_password):
    conn = connect_db()
    c = conn.cursor()
    c.execute("SELECT password FROM master_password WHERE id=1")
    stored_password = c.fetchone()[0]
    key = load_key()
    
    # Decrypt stored password
    decrypted_stored_password = decrypt_password(stored_password, key)

    conn.close()
    
    # Compare decrypted password with input
    return input_password == decrypted_stored_password

# Save account data
def save_data(url, username, password):
    conn = connect_db()
    c = conn.cursor()
    key = load_key()
    encrypted_password = encrypt_password(password, key)

    c.execute("INSERT INTO accounts (url, username, password) VALUES (?, ?, ?)", (url, username, encrypted_password))
    conn.commit()
    conn.close()

# Retrieve account data
def return_password(url):
    conn = connect_db()
    c = conn.cursor()
    key = load_key()

    c.execute("SELECT username, password FROM accounts WHERE url=?", (url,))
    result = c.fetchone()
    if result:
        username, encrypted_password = result
        decrypted_password = decrypt_password(encrypted_password, key)
        conn.close()
        return username, decrypted_password
    else:
        conn.close()
        return None, None

# Main program loop
def main():
    attempts = 0
    while attempts < 3:
        master_password = input("Please enter the Master Password: ")
        if input_validation(master_password) and verify_master_password(master_password):
            print("Login successful.")
            break
        else:
            attempts += 1
            print(f"Invalid password. {3 - attempts} attempts left.")
            if attempts == 3:
                print("Too many failed attempts. Exiting...")
                exit()

    while True:
        print("\n1: Add Account")
        print("2: View Account")
        print("3: Change Master Password")
        print("4: Log out")
        choice = input("Choose an option: ")

        if choice == "1":
            url = input("Enter account URL: ")
            username = input("Enter account username: ")
            password = input("Enter account password: ")
            save_data(url, username, password)
            print("Account saved successfully.")

        elif choice == "2":
            url = input("Enter the URL of the account you want to retrieve: ")
            username, password = return_password(url)
            if username:
                print(f"Username: {username}\nPassword: {password}")
            else:
                print("No account found for that URL.")

        elif choice == "3":
            new_password = input("Enter new master password: ")
            if input_validation(new_password):
                conn = connect_db()
                c = conn.cursor()
                key = load_key()
                encrypted_new_password = encrypt_password(new_password, key)
                c.execute("UPDATE master_password SET password=? WHERE id=1", (encrypted_new_password,))
                conn.commit()
                conn.close()
                print("Master password updated.")
            else:
                print("Invalid password format.")

        elif choice == "4":
            print("Logging out...")
            break

        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()
