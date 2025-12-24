README — Claude Conversations Import in WestMoneyOS (SQLite)

Was das Skript macht
- Legt eigene Tabellen mit Präfix `claude_` an (keine Kollisionen mit deinen App-Tabellen).
- Importiert den Inhalt aus `claude_migrated_export.zip` (enthält `claude_export.sqlite`).
- Ist idempotent (INSERT OR IGNORE): Mehrfach ausführen ist unkritisch.

Tabellen
- claude_conversations
- claude_messages
- claude_message_content
- claude_attachments
- claude_files
- claude_users
- claude_projects
- claude_project_docs
- claude_memories
- claude_project_memories
- claude_import_runs (Protokoll der Imports)

Server-Usage
1) Dateien nach /var/www/westmoney legen:
   - import_claude_to_westmoney.py
   - claude_migrated_export.zip

2) Ausführen:
   cd /var/www/westmoney
   ./venv/bin/python import_claude_to_westmoney.py --input ./claude_migrated_export.zip

3) Falls DB nicht gefunden wird, DB-Pfad explizit:
   ./venv/bin/python import_claude_to_westmoney.py --input ./claude_migrated_export.zip --db ./instance/westmoney.db

Prüfen
   sqlite3 ./instance/westmoney.db "SELECT COUNT(*) FROM claude_messages;"
