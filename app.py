import streamlit as st
import hashlib
import json
import os
import time
from cryptography.fernet import Fernet

# File for saving encrypted data
DATA_FILE = "data.json"

# Load or initialize data
def loaddata():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def savedata(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

data = loaddata()

# Generate app-wide encryption key
if "key" not in st.session_state:
    st.session_state.key = Fernet.generate_key()
cipher = Fernet(st.session_state.key)

# Hash passkey using PBKDF2
def hashpasskey1(passkey, salt):
    return hashlib.pbkdf2_hmac("sha256", passkey.encode(), salt.encode(), 100000).hex()

# UI Title
st.set_page_config(page_title="🔐 Secure Data Vault", page_icon="🛡️")
st.title("🛡️ Secure Data Encryption System")

# Sidebar Navigation
menu = ["Home", "Store Data", "Retrieve Data"]
choice = st.sidebar.radio("📁 Navigate", menu)

# Home Page
if choice == "Home":
    st.subheader("🏠 Welcome to Your Secure Vault")
    st.write("""
    🔐 Store & retrieve data safely using encryption + passkey  
    🔑 Each user is identified by a **username**  
    ⏱️ Locked out for 30 seconds after 3 failed attempts
    """)

# Store Data Page
elif choice == "Store Data":
    st.subheader("📦 Store Encrypted Data")

    username = st.text_input("👤 Enter your username")
    text = st.text_area("🔏 Enter text to encrypt")
    passkey = st.text_input("🔑 Create a passkey", type="password")

    if st.button("🔐 Encrypt & Save"):
        if username and text and passkey:
            salt = os.urandom(16).hex()
            hashed = hashpasskey1(passkey, salt)
            encrypted = cipher.encrypt(text.encode()).decode()

            data[username] = {
                "encrypted_text": encrypted,
                "passkey": hashed,
                "salt": salt,
                "failed_attempts": 0,
                "lockout_time": 0
            }

            savedata(data)
            st.success("✅ Data encrypted and stored successfully!")
            st.code(encrypted, language="text")
        else:
            st.error("⚠️ All fields are required!")

# Retrieve Data Page
elif choice == "Retrieve Data":
    st.subheader("🔍 Retrieve Your Encrypted Data")

    username = st.text_input("👤 Enter your username")
    passkey = st.text_input("🔑 Enter your passkey", type="password")

    if st.button("🔓 Decrypt"):
        if username and passkey:
            user = data.get(username)

            if not user:
                st.error("❌ User not found!")
            else:
                current_time = time.time()
                locked = current_time < user.get("lockout_time", 0)

                if locked:
                    seconds_left = int(user["lockout_time"] - current_time)
                    st.error(f"⏱️ Locked out. Try again in {seconds_left} seconds.")
                else:
                    hashed = hashpasskey1(passkey, user["salt"])
                    if hashed == user["passkey"]:
                        decrypted = cipher.decrypt(user["encrypted_text"].encode()).decode()
                        st.success("✅ Decryption successful!")
                        st.code(decrypted, language="text")
                        user["failed_attempts"] = 0
                        user["lockout_time"] = 0
                        savedata(data)
                    else:
                        user["failed_attempts"] += 1
                        attempts_left = 3 - user["failed_attempts"]

                        if user["failed_attempts"] >= 3:
                            user["lockout_time"] = time.time() + 30  # 30 sec lockout
                            st.error("🔒 Too many failed attempts! Locked for 30 seconds.")
                        else:
                            st.error(f"❌ Incorrect passkey! Attempts left: {attempts_left}")
                        savedata(data)
        else:
            st.error("⚠️ Username and passkey are required!")
else:
    st.error("❌ Invalid choice! Please select a valid option from the sidebar.")





