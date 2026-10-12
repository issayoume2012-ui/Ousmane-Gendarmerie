-- Schéma informatif : app.py crée automatiquement les tables au premier lancement.
CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS records (
 id INTEGER PRIMARY KEY AUTOINCREMENT, module TEXT NOT NULL, reference TEXT,
 title TEXT NOT NULL, event_date TEXT, status TEXT DEFAULT 'Nouveau',
 priority TEXT DEFAULT 'Normale', person TEXT, assigned_to TEXT, summary TEXT,
 actions_done TEXT, actions_pending TEXT, due_date TEXT, notes TEXT,
 created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS people (
 id INTEGER PRIMARY KEY AUTOINCREMENT, full_name TEXT NOT NULL, role TEXT,
 contact TEXT, linked_reference TEXT, notes TEXT, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS documents (
 id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, category TEXT,
 linked_reference TEXT, file_name TEXT NOT NULL, file_path TEXT NOT NULL,
 description TEXT, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS audit_log (
 id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, action TEXT NOT NULL,
 module TEXT, record_id INTEGER, details TEXT, created_at TEXT NOT NULL
);
