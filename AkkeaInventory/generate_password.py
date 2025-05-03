# generate_password.py

import bcrypt

plain_password = input("Enter new password: ")
hashed = bcrypt.hashpw(plain_password.encode(), bcrypt.gensalt())
print("Hashed password:", hashed.decode())
