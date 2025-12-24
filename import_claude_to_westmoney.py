#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Import Claude export (claude_migrated_export.zip) into a SQLite database used by WestMoneyOS.
#
# - Creates dedicated tables prefixed with `claude_` so it will not collide with existing app tables.
# - Designed for SQLite (most common for simple Flask deployments). If you run Postgres/MySQL,
#   adapt the DDL/UPSERT logic accordingly.
#
# Usage:
#   ./venv/bin/python import_claude_to_westmoney.py --input ./claude_migrated_export.zip
#   ./venv/bin/python import_claude_to_westmoney.py --input ./claude_migrated_export.zip --db ./instance/westmoney.db
#
# Exit codes:
#   0 success
#   2 missing input
#   3 missing/unsupported db
#   4 invalid input (zip/sqlite not found)

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import os
import shutil
import sqlite3
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Optional


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def detect_sqlite_db(explicit: Optional[str]) -> Path:
    if explicit:
        return Path(explicit).expanduser().resolve()

    # 1) Try env vars
    for key in ("SQLALCHEMY_DATABASE_URI", "DATABASE_URL", "WESTMONEY_DB", "WESTMONEY_DB_PATH"):
        v = os.environ.get(key)
        if not v:
            continue
        if v.startswith("sqlite:///"):
            raw = v[len("sqlite:///"):]
            if raw.startswith("/"):
                return Path(raw).resolve()
            return (Path.cwd() / raw).resolve()
        if v.startswith("sqlite:////"):
            raw = v[len("sqlite:"):]  # keeps leading slashes
            return Path(raw).resolve()

    # 2) Try common paths
    candidates = [
        Path.cwd() / "instance" / "westmoney.db",
        Path.cwd() / "instance" / "app.db",
        Path.cwd() / "instance" / "database.db",
        Path.cwd() / "westmoney.db",
        Path.cwd() / "app.db",
        Path.cwd() / "database.db",
        Path("/var/www/westmoney/instance/westmoney.db"),
        Path("/var/www/westmoney/instance/app.db"),
        Path("/var/www/westmoney/instance/database.db"),
        Path("/var/www/westmoney/westmoney.db"),
        Path("/var/www/westmoney/app.db"),
        Path("/var/www/westmoney/database.db"),
    ]
    for c in candidates:
        if c.exists():
            return c.resolve()

    raise FileNotFoundError(
        "SQLite DB not found. Pass --db or set SQLALCHEMY_DATABASE_URI=sqlite:///... (only SQLite supported by this script)."
    )


def open_sqlite(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    return conn


def ensure_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS claude_import_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            imported_at TEXT NOT NULL,
            source_sha256 TEXT NOT NULL,
            source_name TEXT NOT NULL,
            notes TEXT
        );

        CREATE TABLE IF NOT EXISTS claude_conversations (
            conversation_uuid TEXT PRIMARY KEY,
            name TEXT,
            created_at TEXT,
            updated_at TEXT,
            messages INTEGER,
            human_messages INTEGER,
            assistant_messages INTEGER,
            text_characters INTEGER
        );

        CREATE TABLE IF NOT EXISTS claude_messages (
            message_uuid TEXT PRIMARY KEY,
            conversation_uuid TEXT NOT NULL,
            message_index INTEGER,
            sender TEXT,
            text TEXT,
            account TEXT,
            message_created_at TEXT,
            message_updated_at TEXT,
            conversation_name TEXT,
            conversation_summary TEXT,
            conversation_created_at TEXT,
            conversation_updated_at TEXT,
            FOREIGN KEY(conversation_uuid) REFERENCES claude_conversations(conversation_uuid) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS claude_message_content (
            conversation_uuid TEXT NOT NULL,
            message_uuid TEXT NOT NULL,
            content_index INTEGER NOT NULL,
            type TEXT,
            text TEXT,
            start_timestamp TEXT,
            stop_timestamp TEXT,
            flags TEXT,
            citations TEXT,
            PRIMARY KEY(message_uuid, content_index),
            FOREIGN KEY(conversation_uuid) REFERENCES claude_conversations(conversation_uuid) ON DELETE CASCADE,
            FOREIGN KEY(message_uuid) REFERENCES claude_messages(message_uuid) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS claude_attachments (
            conversation_uuid TEXT NOT NULL,
            message_uuid TEXT NOT NULL,
            attachment_index INTEGER NOT NULL,
            file_name TEXT,
            file_size INTEGER,
            file_type TEXT,
            extracted_content TEXT,
            PRIMARY KEY(message_uuid, attachment_index),
            FOREIGN KEY(conversation_uuid) REFERENCES claude_conversations(conversation_uuid) ON DELETE CASCADE,
            FOREIGN KEY(message_uuid) REFERENCES claude_messages(message_uuid) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS claude_files (
            conversation_uuid TEXT NOT NULL,
            message_uuid TEXT NOT NULL,
            file_index INTEGER NOT NULL,
            file_name TEXT,
            PRIMARY KEY(message_uuid, file_index),
            FOREIGN KEY(conversation_uuid) REFERENCES claude_conversations(conversation_uuid) ON DELETE CASCADE,
            FOREIGN KEY(message_uuid) REFERENCES claude_messages(message_uuid) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS claude_users (
            uuid TEXT PRIMARY KEY,
            full_name TEXT,
            email_address TEXT,
            verified_phone_number TEXT
        );

        CREATE TABLE IF NOT EXISTS claude_projects (
            uuid TEXT PRIMARY KEY,
            name TEXT,
            description TEXT,
            is_private INTEGER,
            is_starter_project INTEGER,
            prompt_template TEXT,
            created_at TEXT,
            updated_at TEXT,
            creator_uuid TEXT,
            creator_full_name TEXT
        );

        CREATE TABLE IF NOT EXISTS claude_project_docs (
            project_uuid TEXT NOT NULL,
            doc_uuid TEXT NOT NULL,
            filename TEXT,
            created_at TEXT,
            content TEXT,
            PRIMARY KEY(project_uuid, doc_uuid),
            FOREIGN KEY(project_uuid) REFERENCES claude_projects(uuid) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS claude_memories (
            account_uuid TEXT PRIMARY KEY,
            conversations_memory TEXT
        );

        CREATE TABLE IF NOT EXISTS claude_project_memories (
            account_uuid TEXT NOT NULL,
            project_uuid TEXT NOT NULL,
            project_memory TEXT,
            PRIMARY KEY(account_uuid, project_uuid),
            FOREIGN KEY(project_uuid) REFERENCES claude_projects(uuid) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_claude_messages_conv ON claude_messages(conversation_uuid);
        CREATE INDEX IF NOT EXISTS idx_claude_content_conv ON claude_message_content(conversation_uuid);
        CREATE INDEX IF NOT EXISTS idx_claude_attach_conv ON claude_attachments(conversation_uuid);
        """
    )
    conn.commit()


def extract_sqlite_from_zip(zip_path: Path) -> Path:
    if not zip_path.exists():
        raise FileNotFoundError(str(zip_path))

    tmpdir = Path(tempfile.mkdtemp(prefix="claude_import_"))
    with zipfile.ZipFile(zip_path, "r") as z:
        if "claude_export.sqlite" not in z.namelist():
            raise ValueError("Zip does not include 'claude_export.sqlite' (expected migrated export zip).")
        z.extract("claude_export.sqlite", path=tmpdir)
    return tmpdir / "claude_export.sqlite"


def copy_table(
    src: sqlite3.Connection,
    dst: sqlite3.Connection,
    src_table: str,
    insert_sql: str,
    chunk: int = 2000,
) -> int:
    cur = src.cursor()
    cur.execute(f"SELECT * FROM {src_table};")
    n = 0
    rows = cur.fetchmany(chunk)
    while rows:
        dst.executemany(insert_sql, rows)
        n += len(rows)
        rows = cur.fetchmany(chunk)
    return n


def main() -> int:
    ap = argparse.ArgumentParser(description="Import Claude export into WestMoney SQLite DB.")
    ap.add_argument("--input", required=True, help="Path to claude_migrated_export.zip")
    ap.add_argument("--db", required=False, help="Path to WestMoney SQLite DB (optional; auto-detect if omitted)")
    ap.add_argument("--note", required=False, default="", help="Optional note stored in claude_import_runs")
    args = ap.parse_args()

    in_zip = Path(args.input).expanduser().resolve()
    if not in_zip.exists():
        print(f"[ERROR] Input not found: {in_zip}", file=sys.stderr)
        return 2

    try:
        db_path = detect_sqlite_db(args.db)
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 3

    try:
        src_sqlite = extract_sqlite_from_zip(in_zip)
    except Exception as e:
        print(f"[ERROR] Invalid input zip: {e}", file=sys.stderr)
        return 4

    source_hash = sha256_file(in_zip)
    imported_at = _dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

    dst = open_sqlite(db_path)
    ensure_schema(dst)

    src = sqlite3.connect(str(src_sqlite))
    try:
        with dst:
            dst.execute(
                "INSERT INTO claude_import_runs(imported_at, source_sha256, source_name, notes) VALUES (?, ?, ?, ?)",
                (imported_at, source_hash, in_zip.name, args.note or None),
            )

        conv_insert = """
            INSERT OR IGNORE INTO claude_conversations
            (conversation_uuid, name, created_at, updated_at, messages, human_messages, assistant_messages, text_characters)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        msg_insert = """
            INSERT OR IGNORE INTO claude_messages
            (conversation_uuid, conversation_name, conversation_summary, conversation_created_at, conversation_updated_at,
             account, message_index, message_uuid, sender, text, message_created_at, message_updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        content_insert = """
            INSERT OR IGNORE INTO claude_message_content
            (conversation_uuid, message_uuid, content_index, type, text, start_timestamp, stop_timestamp, flags, citations)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        attach_insert = """
            INSERT OR IGNORE INTO claude_attachments
            (conversation_uuid, message_uuid, attachment_index, file_name, file_size, file_type, extracted_content)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        files_insert = """
            INSERT OR IGNORE INTO claude_files
            (conversation_uuid, message_uuid, file_index, file_name)
            VALUES (?, ?, ?, ?)
        """
        users_insert = """
            INSERT OR IGNORE INTO claude_users
            (uuid, full_name, email_address, verified_phone_number)
            VALUES (?, ?, ?, ?)
        """
        projects_insert = """
            INSERT OR IGNORE INTO claude_projects
            (uuid, name, description, is_private, is_starter_project, prompt_template, created_at, updated_at, creator_uuid, creator_full_name)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        pdocs_insert = """
            INSERT OR IGNORE INTO claude_project_docs
            (project_uuid, doc_uuid, filename, created_at, content)
            VALUES (?, ?, ?, ?, ?)
        """
        memories_insert = """
            INSERT OR IGNORE INTO claude_memories
            (account_uuid, conversations_memory)
            VALUES (?, ?)
        """
        pmem_insert = """
            INSERT OR IGNORE INTO claude_project_memories
            (account_uuid, project_uuid, project_memory)
            VALUES (?, ?, ?)
        """

        stats = {}
        with dst:
            stats["conversations"] = copy_table(src, dst, "conversations", conv_insert)
            stats["messages"] = copy_table(src, dst, "messages", msg_insert)
            stats["message_content"] = copy_table(src, dst, "message_content", content_insert)
            stats["attachments"] = copy_table(src, dst, "attachments", attach_insert)
            stats["files"] = copy_table(src, dst, "files", files_insert)
            stats["users"] = copy_table(src, dst, "users", users_insert)
            stats["projects"] = copy_table(src, dst, "projects", projects_insert)
            stats["project_docs"] = copy_table(src, dst, "project_docs", pdocs_insert)
            stats["memories"] = copy_table(src, dst, "memories", memories_insert)
            stats["project_memories"] = copy_table(src, dst, "project_memories", pmem_insert)

        print("[OK] Import complete.")
        print(f"     DB: {db_path}")
        print(f"     Source: {in_zip.name} (sha256 {source_hash[:12]}...)")
        for k, v in stats.items():
            print(f"     {k}: {v} rows inserted/ignored")
        print("     Idempotent via INSERT OR IGNORE + PK/UNIQUE constraints.")
        return 0

    finally:
        try:
            src.close()
        except Exception:
            pass
        try:
            dst.close()
        except Exception:
            pass
        try:
            shutil.rmtree(str(src_sqlite.parent), ignore_errors=True)
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
