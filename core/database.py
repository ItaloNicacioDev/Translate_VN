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

    def execute_many(self, query: str, params_list: list):
        """Executa a mesma query para uma lista de parâmetros dentro
        de UMA única transação/commit, em vez de um commit por linha
        (que é o que torna inserções em massa extremamente lentas no
        SQLite - cada commit força um fsync em disco)."""

        self.cursor.executemany(query, params_list)

        self.commit()

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

    # ===================================================
    # Diálogos (CRUD)
    # ===================================================

    def insert_dialogue(
        self,
        project_id: int,
        file_path: str,
        line: int,
        original: str,
        translated: str = "",
        status: str = "pending"
    ):

        self.execute(
            """
            INSERT INTO dialogues(
                project_id, file_id, character,
                original, translated, status
            )
            VALUES(?,?,?,?,?,?)
            """,
            (
                project_id,
                None,
                file_path + f":{line}",
                original,
                translated,
                status
            )
        )

        return self.cursor.lastrowid

    def insert_dialogues_bulk(self, project_id: int, dialogues: list):
        """Versão em massa de insert_dialogue: insere todos os
        diálogos de uma vez, com um único commit no final, em vez de
        um commit por linha. Para jogos com dezenas de milhares de
        linhas, isso é a diferença entre segundos e vários minutos."""

        rows = [
            (
                project_id,
                None,
                dialogue["file"] + f":{dialogue['line']}",
                dialogue["original"],
                dialogue.get("translated", ""),
                dialogue.get("status", "pending")
            )
            for dialogue in dialogues
        ]

        self.execute_many(
            """
            INSERT INTO dialogues(
                project_id, file_id, character,
                original, translated, status
            )
            VALUES(?,?,?,?,?,?)
            """,
            rows
        )

    def get_dialogues_by_project(self, project_id: int):

        return self.fetch_all(
            "SELECT * FROM dialogues WHERE project_id=? ORDER BY id",
            (project_id,)
        )

    def update_dialogue(
        self,
        dialogue_id: int,
        translated: str,
        status: str = "translated"
    ):

        self.execute(
            "UPDATE dialogues SET translated=?, status=? WHERE id=?",
            (translated, status, dialogue_id)
        )

    def update_dialogues_bulk(self, updates: list):
        """updates: lista de tuplas (translated, status, dialogue_id).
        Mesma ideia do insert_dialogues_bulk: um commit só, não um
        por linha."""

        self.execute_many(
            "UPDATE dialogues SET translated=?, status=? WHERE id=?",
            updates
        )

    def delete_dialogue(self, dialogue_id: int):

        self.execute(
            "DELETE FROM dialogues WHERE id=?",
            (dialogue_id,)
        )

    def clear_dialogues(self, project_id: int):

        self.execute(
            "DELETE FROM dialogues WHERE project_id=?",
            (project_id,)
        )

    def get_dialogue(self, dialogue_id: int):

        return self.fetch_one(
            "SELECT * FROM dialogues WHERE id=?",
            (dialogue_id,)
        )

    def restore_dialogue(self, dialogue_id: int):
        """Apaga a tradução da linha e devolve o status para 'pending'."""

        self.execute(
            "UPDATE dialogues SET translated=?, status=? WHERE id=?",
            ("", "pending", dialogue_id)
        )

    # ===================================================
    # Idiomas (CRUD)
    # ===================================================

    def insert_language(self, code: str, name: str):

        self.execute(
            "INSERT INTO languages(code, name) VALUES(?,?)",
            (code, name)
        )

        return self.cursor.lastrowid

    def get_languages(self):

        return self.fetch_all(
            "SELECT * FROM languages ORDER BY name"
        )

    def get_language(self, language_id: int):

        return self.fetch_one(
            "SELECT * FROM languages WHERE id=?",
            (language_id,)
        )

    def update_language(self, language_id: int, code: str, name: str):

        self.execute(
            "UPDATE languages SET code=?, name=? WHERE id=?",
            (code, name, language_id)
        )

    def delete_language(self, language_id: int):

        self.execute(
            "DELETE FROM languages WHERE id=?",
            (language_id,)
        )

    # ===================================================
    # Configurações (settings) - chave/valor no banco
    # ===================================================

    def set_setting(self, key: str, value: str):

        self.execute(
            """
            INSERT INTO settings(key, value)
            VALUES(?, ?)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value
            """,
            (key, value)
        )

    def get_setting(self, key: str, default=None):

        row = self.fetch_one(
            "SELECT value FROM settings WHERE key=?",
            (key,)
        )

        return row["value"] if row else default

    # ===================================================
    # Projetos (auxiliar)
    # ===================================================

    def get_project_id(self, name: str):

        row = self.fetch_one(
            "SELECT id FROM projects WHERE name=?",
            (name,)
        )

        return row["id"] if row else None