from passlib.hash import bcrypt
from app.domain.ports.password_hasher import PasswordHasher


class BcryptPasswordHasher(PasswordHasher):
    def hash(self, plain: str) -> str:
        return bcrypt.using(rounds=12).hash(plain)

    def verify(self, plain: str, hashed: str) -> bool:
        return bcrypt.verify(plain, hashed)
