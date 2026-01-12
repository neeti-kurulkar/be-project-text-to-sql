import bcrypt

password = "password123"
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12))
print(f"Password: {password}")
print(f"Correct hash: {hashed.decode('utf-8')}")
print("\nRun this SQL in pgAdmin to update all users:")
print(f"UPDATE users SET password_hash = '{hashed.decode('utf-8')}';")
