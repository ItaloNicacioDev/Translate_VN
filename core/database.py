"""
database.py

Gerenciador do banco de dados SQLite.
"""

from pathlib import Path
import sqlite3


class Database:

    def __init__(self, database_path: str = "database.db"):

        self.database_path = Path(database_path)

        self.connection = None
        self.cursor = None

    def connect(self):

        if self.connection is None:

            self.connection = sqlite3.connect(self.database_path)

            self.connection.row_factory = sqlite3.Row

            self.cursor = self.connection.cursor()

        return self.connection

    def close(self):

        if self.connection:

            self.connection.close()

            self.connection = None
            self.cursor = None

    def commit(self):

        if self.connection:
            self.connection.commit()

    def execute(self, query: str, params: tuple = ()):

        self.cursor.execute(query, params)

        self.commit()

    def fetch_one(self, query: str, params: tuple = ()):

        self.cursor.execute(query, params)

        return self.cursor.fetchone()

    def fetch_all(self, query: str, params: tuple = ()):

        self.cursor.execute(query, params)

        return self.cursor.fetchall()

    def create_tables(self):

        self.execute("""
        CREATE TABLE IF NOT EXISTS projects (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            engine TEXT,

            version TEXT,

            game_path TEXT,

            language_original TEXT,

            language_translation TEXT,

            created_at TEXT,

            updated_at TEXT

        )
        """)

        self.execute("""
        CREATE TABLE IF NOT EXISTS files (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            project_id INTEGER,

            filename TEXT,

            filepath TEXT,

            filetype TEXT,

            FOREIGN KEY(project_id)
                REFERENCES projects(id)

        )
        """)

        self.execute("""
        CREATE TABLE IF NOT EXISTS dialogues (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            project_id INTEGER,

            file_id INTEGER,

            character TEXT,

            original TEXT,

            translated TEXT,

            status TEXT,

            FOREIGN KEY(project_id)
                REFERENCES projects(id),

            FOREIGN KEY(file_id)
                REFERENCES files(id)

        )
        """)

        self.execute("""
        CREATE TABLE IF NOT EXISTS languages (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            code TEXT,

            name TEXT

        )
        """)

        self.execute("""
        CREATE TABLE IF NOT EXISTS settings (

            key TEXT PRIMARY KEY,

            value TEXT

        )
        """)

    def initialize(self):

        self.connect()

        self.create_tables()