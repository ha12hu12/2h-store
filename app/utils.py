import bcrypt
import bcrypt

def hash_password(password: str) -> str:
    # convert the password to bytes
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    # hash password
    hashed_password = bcrypt.hashpw(pwd_bytes, salt)
    return hashed_password.decode('utf-8')  # return as str

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        password= plain_password.encode('utf-8'),
        hashed_password= hashed_password.encode('utf-8')
    )