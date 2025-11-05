import hashlib

# Change 'your_new_password' to whatever you want
new_password = 'Password1'  
password_hash = hashlib.sha256(new_password.encode()).hexdigest()
print(f"New password hash: {password_hash}")
