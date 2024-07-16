import hashlib

# 原始密码
password = "admin"

# 使用 SHA-256 进行加密
hashed_password = hashlib.sha256(password.encode()).hexdigest()

print(hashed_password)
