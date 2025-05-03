import bcrypt
import json

users = {
    "admin": {
        "password": bcrypt.hashpw("admin".encode(), bcrypt.gensalt()).decode(),
        "role": "admin"
    },
    "staff": {
        "password": bcrypt.hashpw("staff".encode(), bcrypt.gensalt()).decode(),
        "role": "staff"
    }
}

with open("users.json", "w") as f:
    json.dump(users, f, indent=4)

print("✅ users.json generated with admin and staff accounts.")
