import hashlib
import os
import sqlite3
from contextlib import closing
from pathlib import Path


class AuthService:
    def __init__(self, db_path: str = "payroll.db"):
        self.db_path = Path(db_path)
        self._init_auth_table()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init_auth_table(self):
        with closing(self._connect()) as con, con:
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL
                )
                """
            )

    @staticmethod
    def _hash_password(password: str, salt: str) -> str:
        return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()

    def register(self, username: str, password: str) -> None:
        if len(username.strip()) < 4:
            raise ValueError("Логин должен быть не короче 4 символов")
        if len(password) < 8:
            raise ValueError("Пароль должен быть не короче 8 символов")
        salt = os.urandom(16).hex()
        password_hash = self._hash_password(password, salt)

        try:
            with closing(self._connect()) as con, con:
                con.execute(
                    "INSERT INTO users(username, password_hash, salt) VALUES (?, ?, ?)",
                    (username.strip(), password_hash, salt),
                )
        except sqlite3.IntegrityError as err:
            raise ValueError("Пользователь с таким логином уже существует") from err

    def authenticate(self, username: str, password: str) -> bool:
        with closing(self._connect()) as con:
            row = con.execute(
                "SELECT password_hash, salt FROM users WHERE username=?", (username.strip(),)
            ).fetchone()

        if not row:
            return False
        expected_hash, salt = row
        return expected_hash == self._hash_password(password, salt)
