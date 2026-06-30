# auth.py - Simplified
import streamlit as st
import hashlib

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def login(username: str, password: str) -> bool:
    if not username or not password:
        return False
    
    demo_users = {
        "admin": "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918",
        "operator": "5a105e8b9d40e1329780d62ea2265d8a",
        "manager": "8d969eef6ecad3c29a3a873fb1a8c67e"
    }
    
    stored_hash = demo_users.get(username, "")
    provided_hash = hash_password(password)
    
    return stored_hash == provided_hash
    except:
        pass
