from passlib.context import CryptContext
import bcrypt

print(f"Bcrypt version: {bcrypt.__version__}")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

password = "password123"
print(f"Testing password: {password} (len: {len(password)})")

try:
    hashed = pwd_context.hash(password)
    print(f"Hashed: {hashed}")
except Exception as e:
    print(f"Error hashing with passlib: {e}")

try:
    # Direct bcrypt test
    salt = bcrypt.gensalt()
    hashed_direct = bcrypt.hashpw(password.encode('utf-8'), salt)
    print(f"Direct bcrypt hashed: {hashed_direct}")
except Exception as e:
    print(f"Error hashing with direct bcrypt: {e}")
