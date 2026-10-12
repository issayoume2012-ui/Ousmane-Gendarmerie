import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor
import hashlib
import hmac
import os
import json
import csv
import io
import shutil
import secrets
import re
from pathlib import Path
from datetime import datetime, date, timedelta
import pandas as pd

APP_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.environ.get("GENDARMERIE_DESK_DATA", APP_DIR / "data"))
UPLOAD_DIR = DATA_DIR / "documents"
BACKUP_DIR = DATA_DIR / "backups"
DB_PATH = "Supabase PostgreSQL"
for folder in (DATA_DIR, UPLOAD_DIR, BACKUP_DIR):
    folder.mkdir(parents=True, exist_ok=True)

st.set_page_config(page_title="Sergent Ousmane Youm", page_icon="🇸🇳", layout="wide", initial_sidebar_state="collapsed")

# ---------- Styles ----------
st.markdown("""
<style>
/* Masquer la barre Streamlit (Share, étoile, édition, GitHub et menu). */
[data-testid="stToolbar"],
[data-testid="stHeaderActionElements"],
[data-testid="stStatusWidget"],
#MainMenu,
header[data-testid="stHeader"] button,
header[data-testid="stHeader"] a { visibility:hidden !important; display:none !important; }
[data-testid="stHeader"] { height:0 !important; min-height:0 !important; }
:root { --navy:#08172c; --blue:#173b68; --gold:#d6b35d; --green:#00853f; --red:#e31b23; }
.stApp { background: linear-gradient(135deg,#f4f7fb 0%,#eef2f8 100%); }
.block-container { padding-top: 1.3rem; padding-bottom: 2rem; max-width: 1500px; }
.hero { position:relative; overflow:hidden; background:radial-gradient(circle at 90% 15%,#315784 0%,transparent 32%),linear-gradient(120deg,#071326,#153a66 65%,#102947); padding:1.2rem 1.4rem; border-radius:22px; color:white; box-shadow:0 15px 38px #0b17302b; margin-bottom:1rem; border:1px solid #d6b35d; border-bottom:5px solid #d6b35d; }
.hero h1 { margin:0; font-size:2rem; letter-spacing:.08em; color:white; font-weight:850; }
.hero p { margin:.35rem 0 0 0; color:#e2eaf5; }
.brand-row {display:flex;align-items:center;gap:1rem;}
.brand-seal {flex:0 0 76px;width:76px;height:76px;border-radius:50%;background:#fff;border:4px solid #d6b35d;display:flex;align-items:center;justify-content:center;box-shadow:0 5px 16px #0003;color:#0b1730;font-weight:900;font-size:1.05rem;text-align:center;line-height:1.05;}
.brand-seal small {font-size:.55rem;display:block;letter-spacing:.05em;}
.brand-seal.mfa {background:linear-gradient(145deg,#fff,#e9eef6);border-color:#8fa7c2;color:#173b68;font-size:.92rem;}
.brand-seal.mfa small {font-size:.48rem;}
.flag-sn {display:flex;width:76px;height:48px;border-radius:7px;overflow:hidden;border:1px solid #ffffffa0;box-shadow:0 4px 12px #0003;flex:0 0 76px;}
.flag-sn span {flex:1;} .flag-sn .fg {background:#00853f;position:relative;} .flag-sn .fy {background:#fdef42;display:flex;align-items:center;justify-content:center;color:#00853f;font-size:1.25rem;} .flag-sn .fr {background:#e31b23;}
.brand-identity {display:flex;flex-direction:column;gap:.55rem;min-width:0;}
.brand-kicker {font-size:.74rem;text-transform:uppercase;letter-spacing:.13em;font-weight:800;color:#f4d78a;}
.brand-subtitle {font-size:.92rem;color:#e2eaf5;line-height:1.45;}
.brand-pills {display:flex;flex-wrap:wrap;gap:.4rem;margin-top:.6rem;}
.brand-pill {border:1px solid #ffffff45;background:#ffffff12;border-radius:999px;padding:.32rem .65rem;font-size:.72rem;font-weight:700;color:#f7f9fc;}
.export-note {border-left:4px solid #d6b35d;background:#f4f7fb;padding:.65rem .85rem;border-radius:7px;color:#34465f;font-size:.88rem;margin-bottom:.8rem;}
.metric-card { background:white; padding:1rem 1.1rem; border-radius:16px; border:1px solid #e1e8f1; box-shadow:0 5px 18px #142a4510; min-height:112px; }
.metric-label { color:#63738a; font-size:.9rem; }
.metric-value { color:#102544; font-size:2rem; font-weight:750; margin-top:.15rem; }
.section-head { color:#132c4d; font-weight:750; font-size:1.2rem; margin:.4rem 0 .8rem; }
div[data-testid="stSidebar"] { background:#0b1730; }
div[data-testid="stSidebar"] * { color:#f2f6fb; }
div[data-testid="stSidebar"] button { border-radius:10px; }
.stButton button, .stDownloadButton button { border-radius:10px; font-weight:600; }
div[data-testid="stForm"] { background:#ffffff; padding:1rem; border-radius:14px; border:1px solid #e1e8f1; }
.small-note { color:#62718a; font-size:.85rem; }
.topnav-wrap { background:linear-gradient(115deg,#0b1730,#173e6b); padding:.65rem .8rem .25rem; border-radius:17px; border:1px solid #c7a45b; box-shadow:0 8px 24px #0b173022; margin-bottom:.55rem; }
.nav-caption { color:#e7edf6; font-size:.75rem; font-weight:700; letter-spacing:.12em; text-transform:uppercase; margin:.1rem 0 .3rem .25rem; }
.subnav-wrap { background:#fff; padding:.55rem .65rem .1rem; border-radius:14px; border:1px solid #dce5f0; box-shadow:0 5px 16px #142a450c; margin-bottom:1rem; }
.footer-panel { background:linear-gradient(115deg,#0b1730,#173e6b); color:#f2f6fb; border-radius:18px; padding:1.2rem 1.35rem; margin-top:1.8rem; border-top:4px solid #c7a45b; box-shadow:0 8px 24px #0b173020; }
.footer-panel h3 { color:#fff; margin:0 0 .45rem 0; }
.footer-panel p { color:#e0e8f4; margin:.3rem 0; line-height:1.55; }
.footer-grid { display:grid; grid-template-columns:2fr 1fr; gap:1.2rem; }
.footer-bottom { border-top:1px solid #ffffff35; margin-top:.8rem; padding-top:.65rem; font-size:.78rem; color:#d5dfed; }
@media(max-width:700px) { .footer-grid { grid-template-columns:1fr; } .hero h1 {font-size:1.35rem;} .brand-row{align-items:flex-start;gap:.65rem;} .brand-seal{width:58px;height:58px;flex-basis:58px;font-size:.82rem;} .brand-seal.mfa{font-size:.72rem;} .flag-sn{width:54px;height:35px;flex-basis:54px;} .brand-subtitle{font-size:.8rem;} }
</style>
""", unsafe_allow_html=True)

# ---------- Database : Supabase PostgreSQL (tables/indexes créés automatiquement au démarrage) ----------
def _postgres_config():
    """Charge les paramètres depuis DATABASE_URL ou .streamlit/secrets.toml.
    Ne jamais enregistrer le mot de passe directement dans le code source.
    """
    dsn = os.environ.get("DATABASE_URL", "").strip()
    if dsn:
        return {"dsn": dsn}
    try:
        pg = st.secrets.get("postgres", {})
        if pg and pg.get("password"):
            return {
                "host": pg.get("host", "aws-0-eu-west-1.pooler.supabase.com"),
                "port": int(pg.get("port", 5432)),
                "dbname": pg.get("database", "postgres"),
                "user": pg.get("user", "postgres.tydfcnfrihfxiuuodhdq"),
                "password": pg.get("password"),
                "sslmode": "require",
                "connect_timeout": 12,
            }
        dsn = str(st.secrets.get("DATABASE_URL", "")).strip()
        if dsn:
            return {"dsn": dsn}
    except Exception:
        pass
    raise RuntimeError(
        "Connexion Supabase non configurée. Ajoutez DATABASE_URL dans les variables "
        "d'environnement ou la section [postgres] dans .streamlit/secrets.toml."
    )

class _CursorCompat:
    def __init__(self, cursor, lastrowid=None):
        self._cursor = cursor
        self.lastrowid = lastrowid
    def fetchone(self): return self._cursor.fetchone()
    def fetchall(self): return self._cursor.fetchall()
    def fetchmany(self, size=None): return self._cursor.fetchmany(size) if size else self._cursor.fetchmany()
    @property
    def rowcount(self): return self._cursor.rowcount
    @property
    def description(self): return self._cursor.description
    def __iter__(self): return iter(self._cursor)

class _ConnectionCompat:
    """Petite couche de compatibilité pour conserver les appels SQL existants."""
    def __init__(self):
        cfg = _postgres_config()
        if "dsn" in cfg:
            self._con = psycopg2.connect(cfg["dsn"], sslmode="require", connect_timeout=12, cursor_factory=RealDictCursor)
        else:
            self._con = psycopg2.connect(**cfg, cursor_factory=RealDictCursor)
    def execute(self, sql, params=()):
        sql = sql.replace("?", "%s")
        # Les endroits du programme qui ont besoin d'un nouvel identifiant le récupèrent
        # via lastrowid : PostgreSQL utilise RETURNING id à la place.
        table = None
        import re as _re
        m = _re.match(r"\s*INSERT\s+INTO\s+([a-zA-Z_][a-zA-Z0-9_]*)", sql, _re.I)
        if m: table = m.group(1).lower()
        wants_id = table in {"records", "questionnaires", "people", "documents"} and "RETURNING" not in sql.upper()
        cur = self._con.cursor()
        if wants_id:
            cur.execute(sql.rstrip().rstrip(";") + " RETURNING id", params)
            row = cur.fetchone()
            return _CursorCompat(cur, row["id"] if row else None)
        cur.execute(sql, params)
        return _CursorCompat(cur)
    def executescript(self, script):
        cur = self._con.cursor()
        for statement in script.split(";"):
            statement = statement.strip()
            if statement:
                cur.execute(statement)
        cur.close()
    def commit(self): self._con.commit()
    def rollback(self): self._con.rollback()
    def close(self): self._con.close()
    def __enter__(self): return self
    def __exit__(self, exc_type, exc, tb):
        try:
            if exc_type is None: self._con.commit()
            else: self._con.rollback()
        finally: self._con.close()
        return False

def connect():
    return _ConnectionCompat()

def init_db():
    with connect() as con:
        con.executescript("""
        -- Registre de version du schéma : les tables sont créées/actualisées par l'application.
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version INTEGER PRIMARY KEY,
            description TEXT NOT NULL,
            applied_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY, value TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS records (
            id BIGSERIAL PRIMARY KEY,
            module TEXT NOT NULL,
            reference TEXT,
            title TEXT NOT NULL,
            event_date TEXT,
            status TEXT DEFAULT 'Nouveau',
            priority TEXT DEFAULT 'Normale',
            person TEXT,
            assigned_to TEXT,
            summary TEXT,
            actions_done TEXT,
            actions_pending TEXT,
            due_date TEXT,
            notes TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS people (
            id BIGSERIAL PRIMARY KEY,
            full_name TEXT NOT NULL,
            role TEXT,
            contact TEXT,
            linked_reference TEXT,
            notes TEXT,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS documents (
            id BIGSERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            category TEXT,
            linked_reference TEXT,
            file_name TEXT NOT NULL,
            file_path TEXT NOT NULL,
            description TEXT,
            url TEXT DEFAULT '',
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS questionnaires (
            id BIGSERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            module TEXT NOT NULL,
            description TEXT DEFAULT '',
            questions_json TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'À compléter',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS questionnaire_responses (
            id BIGSERIAL PRIMARY KEY,
            questionnaire_id BIGINT NOT NULL REFERENCES questionnaires(id) ON DELETE CASCADE,
            respondent TEXT DEFAULT '',
            answers_json TEXT NOT NULL,
            notes TEXT DEFAULT '',
            completed_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS audit_log (
            id BIGSERIAL PRIMARY KEY,
            username TEXT,
            action TEXT NOT NULL,
            module TEXT,
            record_id BIGINT,
            details TEXT,
            created_at TEXT NOT NULL
        );
        ALTER TABLE documents ADD COLUMN IF NOT EXISTS url TEXT DEFAULT '';
        CREATE INDEX IF NOT EXISTS idx_records_module ON records(module);
        CREATE INDEX IF NOT EXISTS idx_records_event_date ON records(event_date);
        CREATE INDEX IF NOT EXISTS idx_records_due_date ON records(due_date);
        CREATE INDEX IF NOT EXISTS idx_people_full_name ON people(full_name);
        CREATE INDEX IF NOT EXISTS idx_documents_category ON documents(category);
        CREATE INDEX IF NOT EXISTS idx_questionnaires_module ON questionnaires(module);
        CREATE INDEX IF NOT EXISTS idx_responses_questionnaire ON questionnaire_responses(questionnaire_id);
        CREATE INDEX IF NOT EXISTS idx_audit_log_created_at ON audit_log(created_at);
        """)
        # Marque le schéma comme initialisé. Les INSERT restent idempotents.
        con.execute(
            "INSERT INTO schema_migrations(version, description, applied_at) VALUES(?,?,?) "
            "ON CONFLICT(version) DO NOTHING",
            (1, "Création automatique du schéma GENDARMERIE DESK", datetime.now().isoformat(timespec="seconds")),
        )


def now_iso():
    return datetime.now().isoformat(timespec="seconds")

def get_setting(key, default=None):
    with connect() as con:
        row = con.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        return row["value"] if row else default

def set_setting(key, value):
    with connect() as con:
        con.execute("INSERT INTO settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, str(value)))
        con.commit()

def hash_password(password, salt=None):
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 310000).hex()
    return f"{salt}${digest}"

def verify_password(password, encoded):
    try:
        salt, digest = encoded.split("$", 1)
        candidate = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 310000).hex()
        return hmac.compare_digest(candidate, digest)
    except Exception:
        return False

def audit(action, module=None, record_id=None, details=""):
    username = st.session_state.get("username", "configuration")
    with connect() as con:
        con.execute("INSERT INTO audit_log(username,action,module,record_id,details,created_at) VALUES(?,?,?,?,?,?)",
                    (username, action, module, record_id, str(details)[:1000], now_iso()))
        con.commit()

try:
    init_db()
except Exception as db_error:
    st.error("Connexion à Supabase PostgreSQL impossible.")
    st.markdown("Vérifiez la section `[postgres]` de `.streamlit/secrets.toml` ou la variable d’environnement `DATABASE_URL`.")
    st.code('''[postgres]
host = "aws-0-eu-west-1.pooler.supabase.com"
port = 5432
database = "postgres"
user = "postgres.tydfcnfrihfxiuuodhdq"
password = "VOTRE_NOUVEAU_MOT_DE_PASSE"
''', language="toml")
    st.caption("Détail technique masqué pour éviter d’exposer des informations de connexion. Vérifiez les secrets et les journaux privés du déploiement.")
    st.stop()

# ---------- Authentication: first-run setup ----------
def setup_screen():
    st.markdown('<div class="hero"><div class="brand-row"><div class="brand-seal">GN<small>SÉNÉGAL</small></div><div class="brand-seal mfa">MFA<small>FORCES ARMÉES</small></div><div class="brand-identity"><div class="brand-kicker">République du Sénégal · Un Peuple – Un But – Une Foi</div><h1>SERGENT OUSMANE YOUM</h1><div class="brand-subtitle">Ministère des Forces armées · Gendarmerie nationale<br>Assistant personnel de travail du Sergent Ousmane Youm</div><div class="brand-pills"><span class="brand-pill">SÉCURITÉ</span><span class="brand-pill">TRAÇABILITÉ</span><span class="brand-pill">ORGANISATION DU SERVICE</span></div></div><div class="flag-sn" aria-label="Drapeau du Sénégal"><span class="fg"></span><span class="fy">★</span><span class="fr"></span></div></div></div>', unsafe_allow_html=True)
    st.info("Première utilisation : créez votre compte administrateur. Aucun mot de passe par défaut n'est installé.")
    with st.form("initial_setup"):
        username = st.text_input("Nom d'utilisateur", value="admin")
        password = st.text_input("Créer un mot de passe", type="password")
        confirm = st.text_input("Confirmer le mot de passe", type="password")
        submitted = st.form_submit_button("Créer le compte et continuer", type="primary", use_container_width=True)
    if submitted:
        if len(username.strip()) < 3:
            st.error("Le nom d'utilisateur doit contenir au moins 3 caractères.")
        elif len(password) < 12:
            st.error("Choisissez un mot de passe d'au moins 12 caractères.")
        elif password != confirm:
            st.error("Les deux mots de passe ne correspondent pas.")
        else:
            set_setting("username", username.strip())
            set_setting("password_hash", hash_password(password))
            audit("Création du compte initial", "Sécurité", details="Compte administrateur initial créé")
            st.session_state["username"] = username.strip()
            st.session_state["authenticated"] = True
            st.rerun()

def login_screen():
    st.markdown('<div class="hero"><div class="brand-row"><div class="brand-seal">GN<small>SÉNÉGAL</small></div><div class="brand-seal mfa">MFA<small>FORCES ARMÉES</small></div><div class="brand-identity"><div class="brand-kicker">République du Sénégal · Un Peuple – Un But – Une Foi</div><h1>SERGENT OUSMANE YOUM</h1><div class="brand-subtitle">Ministère des Forces armées · Gendarmerie nationale<br>Assistant personnel de travail • Enquêtes • Activités • Rapports</div></div><div class="flag-sn" aria-label="Drapeau du Sénégal"><span class="fg"></span><span class="fy">★</span><span class="fr"></span></div></div></div>', unsafe_allow_html=True)
    st.markdown("### Connexion")
    with st.form("login"):
        username = st.text_input("Nom d'utilisateur")
        password = st.text_input("Mot de passe", type="password")
        submit = st.form_submit_button("Se connecter", type="primary", use_container_width=True)
    if submit:
        stored_user = get_setting("username", "")
        stored_hash = get_setting("password_hash", "")
        if username == stored_user and verify_password(password, stored_hash):
            st.session_state["authenticated"] = True
            st.session_state["username"] = username
            audit("Connexion réussie", "Sécurité")
            st.rerun()
        else:
            st.error("Identifiants incorrects.")
    st.caption("Application de démonstration et de gestion administrative. Ne pas y saisir de données opérationnelles ou judiciaires sensibles sans validation de l'hébergement et des règles de sécurité.")

if not get_setting("password_hash"):
    setup_screen()
    st.stop()
if not st.session_state.get("authenticated"):
    login_screen()
    st.stop()

# ---------- Helpers ----------
MODULES = {
    "🔎 Enquêtes": ("Enquêtes", ["Nouveau", "En cours", "En attente", "Transmis", "Clôturé"]),
    "📝 Auditions et actes": ("Auditions", ["À programmer", "Programmée", "Réalisée", "Reportée", "Annulée"]),
    "🎖️ Activités de service": ("Activités de service", ["À faire", "En cours", "Réalisée", "Reportée"]),
    "📅 Agenda et échéances": ("Agenda", ["Prévu", "Réalisé", "Reporté", "Annulé"]),
    "📋 Consignes administratives": ("Consignes", ["À traiter", "En cours", "Exécutée", "Transmise"]),
    "👨‍✈️ Encadrement": ("Encadrement", ["À suivre", "En cours", "Terminé"]),
    "🎒 Matériel autorisé": ("Matériel", ["Disponible", "À vérifier", "Maintenance", "Indisponible"]),
    "📚 Formation": ("Formation", ["À programmer", "Programmée", "En cours", "Terminée"]),
    "📄 Rapports": ("Rapports", ["Brouillon", "À vérifier", "Finalisé", "Transmis"]),
}
ALL_STATUSES = sorted({s for _, statuses in MODULES.values() for s in statuses} | {"Nouveau", "En cours", "Clôturé"})

def fetch_records(module=None):
    with connect() as con:
        if module:
            rows = con.execute("SELECT * FROM records WHERE module=? ORDER BY COALESCE(event_date,'' ) DESC, id DESC", (module,)).fetchall()
        else:
            rows = con.execute("SELECT * FROM records ORDER BY updated_at DESC, id DESC").fetchall()
    return [dict(r) for r in rows]

def fetch_people():
    with connect() as con:
        return [dict(r) for r in con.execute("SELECT * FROM people ORDER BY full_name").fetchall()]

def fetch_documents():
    with connect() as con:
        return [dict(r) for r in con.execute("SELECT * FROM documents ORDER BY id DESC").fetchall()]

def insert_record(data):
    stamp = now_iso()
    fields = ["module","reference","title","event_date","status","priority","person","assigned_to","summary","actions_done","actions_pending","due_date","notes","created_at","updated_at"]
    vals = [data.get(f, "") for f in fields[:-2]] + [stamp, stamp]
    with connect() as con:
        cur = con.execute(f"INSERT INTO records({','.join(fields)}) VALUES({','.join(['?']*len(fields))})", vals)
        con.commit()
        rid = cur.lastrowid
    audit("Création", data.get("module"), rid, data.get("title", ""))
    return rid

def update_record(rid, data):
    fields = ["module","reference","title","event_date","status","priority","person","assigned_to","summary","actions_done","actions_pending","due_date","notes"]
    vals = [data.get(f, "") for f in fields]
    vals.extend([now_iso(), int(rid)])
    with connect() as con:
        con.execute(f"UPDATE records SET {','.join(f'{f}=?' for f in fields)}, updated_at=? WHERE id=?", vals)
        con.commit()
    audit("Modification", data.get("module"), rid, data.get("title", ""))

def delete_record(rid):
    with connect() as con:
        row = con.execute("SELECT module,title FROM records WHERE id=?", (int(rid),)).fetchone()
        con.execute("DELETE FROM records WHERE id=?", (int(rid),))
        con.commit()
    audit("Suppression", row["module"] if row else "", rid, row["title"] if row else "")

def record_form(module, statuses, key_prefix, existing=None):
    existing = existing or {}
    def val(k, default=""):
        return existing.get(k, default) or default
    with st.form(f"{key_prefix}_form"):
        c1, c2 = st.columns(2)
        reference = c1.text_input("Référence interne", value=val("reference"), help="Évitez d'y inscrire des identifiants sensibles.")
        title = c2.text_input("Intitulé *", value=val("title"))
        c3, c4, c5 = st.columns(3)
        event_date = c3.date_input("Date", value=date.fromisoformat(val("event_date")) if val("event_date") else date.today())
        status = c4.selectbox("Statut", statuses, index=statuses.index(val("status")) if val("status") in statuses else 0)
        priority = c5.selectbox("Priorité", ["Basse", "Normale", "Haute"], index=["Basse","Normale","Haute"].index(val("priority")) if val("priority") in ["Basse","Normale","Haute"] else 1)
        c6, c7 = st.columns(2)
        person = c6.text_input("Personne / service associé (si nécessaire)", value=val("person"))
        assigned_to = c7.text_input("Responsable du suivi", value=val("assigned_to"))
        summary = st.text_area("Résumé administratif", value=val("summary"), height=100)
        c8, c9 = st.columns(2)
        actions_done = c8.text_area("Actions réalisées", value=val("actions_done"), height=100)
        actions_pending = c9.text_area("Actions à suivre", value=val("actions_pending"), height=100)
        due_value = val("due_date")
        due_date = st.date_input("Échéance", value=date.fromisoformat(due_value) if due_value else date.today(), key=f"{key_prefix}_due")
        notes = st.text_area("Observations", value=val("notes"), height=80)
        saved = st.form_submit_button("Enregistrer", type="primary", use_container_width=True)
    if saved:
        if not title.strip():
            st.error("L'intitulé est obligatoire.")
        else:
            data = {"module": module, "reference": reference.strip(), "title": title.strip(),
                    "event_date": event_date.isoformat(), "status": status, "priority": priority,
                    "person": person.strip(), "assigned_to": assigned_to.strip(), "summary": summary.strip(),
                    "actions_done": actions_done.strip(), "actions_pending": actions_pending.strip(),
                    "due_date": due_date.isoformat(), "notes": notes.strip()}
            if existing:
                update_record(existing["id"], data)
            else:
                insert_record(data)
            st.success("Enregistrement effectué.")
            st.rerun()

# Vocabulaire unique des exports : les noms techniques de la base ne sortent pas dans les documents.
EXPORT_LABELS = {
    "id":"Identifiant", "module":"Rubrique", "reference":"Référence", "title":"Intitulé",
    "event_date":"Date de l’activité", "status":"État", "priority":"Priorité",
    "person":"Personne ou service associé", "assigned_to":"Responsable du suivi",
    "summary":"Résumé administratif", "actions_done":"Actions réalisées",
    "actions_pending":"Actions à suivre", "due_date":"Échéance", "notes":"Observations",
    "created_at":"Date de création", "updated_at":"Dernière modification",
    "full_name":"Nom complet", "role":"Qualité ou rôle", "contact":"Coordonnées",
    "linked_reference":"Référence associée", "category":"Catégorie", "file_name":"Nom du fichier",
    "file_path":"Emplacement du fichier", "description":"Description", "url":"Lien associé",
    "key":"Paramètre", "value":"Valeur", "username":"Utilisateur", "action":"Action effectuée",
    "record_id":"Identifiant de la fiche", "details":"Détails de l’action",
    "questionnaire_id":"Identifiant du questionnaire", "respondent":"Répondant",
    "answers_json":"Réponses", "questions_json":"Questions", "completed_at":"Date de réponse",
    "applied_at":"Date d’application", "version":"Version", "description":"Description",
}
EXPORT_VALUES = {
    "New":"Nouveau", "In progress":"En cours", "Pending":"En attente", "Closed":"Clôturé",
    "Completed":"Terminé", "Cancelled":"Annulé", "Scheduled":"Programmé", "Draft":"Brouillon",
    "Normal":"Normale", "High":"Haute", "Low":"Basse", "Yes":"Oui", "No":"Non",
}

def dataframe_for_export(rows):
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows).drop(columns=["created_at", "updated_at"], errors="ignore")
    df = df.rename(columns={col: EXPORT_LABELS.get(str(col), str(col).replace("_", " ").capitalize()) for col in df.columns})
    # Traduire les valeurs anglaises usuelles sans altérer les textes rédigés par l’utilisateur.
    return df.replace(EXPORT_VALUES)

@st.cache_data(show_spinner=False, max_entries=12, ttl=300)
def _excel_export_bytes(columns, rows):
    frame = pd.DataFrame(rows, columns=columns)
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        frame.to_excel(writer, index=False, sheet_name="Données")
        ws = writer.sheets["Données"]
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions
        for col_cells in ws.columns:
            max_len = min(max((len(str(cell.value or "")) for cell in col_cells), default=12) + 2, 42)
            ws.column_dimensions[col_cells[0].column_letter].width = max(12, max_len)
    return buf.getvalue()

@st.cache_data(show_spinner=False, max_entries=12, ttl=300)
def _word_export_bytes(columns, rows, prefix):
    from docx import Document
    from docx.shared import Inches, RGBColor
    frame = pd.DataFrame(rows, columns=columns).fillna("").astype(str)
    document = Document()
    section = document.sections[0]
    section.top_margin = Inches(0.55)
    section.bottom_margin = Inches(0.55)
    heading = document.add_heading("Sergent Ousmane Youm", 0)
    heading.runs[0].font.color.rgb = RGBColor(22, 59, 104)
    document.add_paragraph("RÉPUBLIQUE DU SÉNÉGAL — MINISTÈRE DES FORCES ARMÉES — GENDARMERIE NATIONALE")
    document.add_heading(f"Export : {str(prefix).replace('_', ' ').title()}", level=1)
    document.add_paragraph(f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}")
    table = document.add_table(rows=1, cols=max(1, len(frame.columns)))
    table.style = "Table Grid"
    for i, col in enumerate(frame.columns):
        table.rows[0].cells[i].text = str(col)
    for _, row in frame.iterrows():
        cells = table.add_row().cells
        for i, col in enumerate(frame.columns):
            cells[i].text = str(row[col])
    buf = io.BytesIO()
    document.save(buf)
    return buf.getvalue()

@st.cache_data(show_spinner=False, max_entries=12, ttl=300)
def _pdf_export_bytes(columns, rows, prefix):
    from xml.sax.saxutils import escape
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import landscape, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    frame = pd.DataFrame(rows, columns=columns).fillna("").astype(str)
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=landscape(A4), rightMargin=0.65*cm, leftMargin=0.65*cm, topMargin=0.8*cm, bottomMargin=0.8*cm)
    styles = getSampleStyleSheet()
    cell_style = ParagraphStyle("CellFR", parent=styles["BodyText"], fontName="Helvetica", fontSize=6.5, leading=8)
    story = [Paragraph("Sergent Ousmane Youm", styles["Title"]),
             Paragraph("RÉPUBLIQUE DU SÉNÉGAL — MINISTÈRE DES FORCES ARMÉES — GENDARMERIE NATIONALE", styles["Normal"]),
             Spacer(1, 0.25*cm),
             Paragraph(f"Export : {escape(str(prefix).replace('_', ' ').title())} · {datetime.now().strftime('%d/%m/%Y à %H:%M')}", styles["Heading2"]),
             Spacer(1, 0.2*cm)]
    # Le PDF privilégie la lisibilité : 250 lignes au maximum et 8 colonnes ; Excel/Word gardent tout.
    subset = frame.head(250)
    cols = list(subset.columns)[:8]
    data = [[Paragraph(escape(str(c)), cell_style) for c in cols]]
    for _, row in subset.iterrows():
        data.append([Paragraph(escape(str(row[c])[:500]), cell_style) for c in cols])
    available_width = landscape(A4)[0] - 1.3*cm
    widths = [available_width / max(1, len(cols))] * len(cols)
    table = Table(data, colWidths=widths, repeatRows=1, splitByRow=1)
    table.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#163b68")),
        ("TEXTCOLOR",(0,0),(-1,0),colors.white), ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ("GRID",(0,0),(-1,-1),0.25,colors.HexColor("#aab7c8")), ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#eef3f8")]),
        ("LEFTPADDING",(0,0),(-1,-1),3), ("RIGHTPADDING",(0,0),(-1,-1),3),
        ("TOPPADDING",(0,0),(-1,-1),3), ("BOTTOMPADDING",(0,0),(-1,-1),3),
    ]))
    story.append(table)
    if len(frame) > 250 or len(frame.columns) > 8:
        story += [Spacer(1, 0.2*cm), Paragraph("Pour obtenir toutes les lignes et toutes les colonnes, utilisez l’export Excel ou Word.", styles["Normal"])]
    doc.build(story)
    return buf.getvalue()

def export_buttons(df, prefix):
    """Génère des exports en français. Les fichiers sont mis en cache pour accélérer les ré-exécutions."""
    if df is None or df.empty:
        st.caption("Aucune donnée à exporter pour le moment.")
        return
    # Garantir un libellé français même si un appel transmet encore des colonnes techniques.
    df = df.copy().rename(columns={col: EXPORT_LABELS.get(str(col), str(col).replace("_", " ").capitalize()) for col in df.columns})
    df = df.replace(EXPORT_VALUES).fillna("")
    columns = tuple(str(c) for c in df.columns)
    rows = tuple(tuple(str(v) for v in row) for row in df.itertuples(index=False, name=None))
    st.markdown('<div class="export-note">Formats de téléchargement : <strong>PDF · Word (.docx) · Excel (.xlsx)</strong>. Documents générés en français.</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    try:
        xlsx = _excel_export_bytes(columns, rows)
        c1.download_button("📊 Télécharger Excel", xlsx, f"{prefix}.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
    except Exception:
        c1.error("La création du fichier Excel a échoué. Réessayez ou contactez le responsable technique.")
    try:
        word = _word_export_bytes(columns, rows, prefix)
        c2.download_button("📝 Télécharger Word", word, f"{prefix}.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)
    except Exception:
        c2.error("La création du fichier Word a échoué. Vérifiez la dépendance python-docx.")
    try:
        pdf = _pdf_export_bytes(columns, rows, prefix)
        c3.download_button("📕 Télécharger PDF", pdf, f"{prefix}.pdf", "application/pdf", use_container_width=True)
    except Exception:
        c3.error("La création du fichier PDF a échoué. Vérifiez la dépendance reportlab.")

def show_records_module(label, module, statuses):
    st.markdown(f'<div class="section-head">{label}</div>', unsafe_allow_html=True)
    tabs = st.tabs(["➕ Nouvel enregistrement", "📋 Consulter / modifier", "📤 Exports"])
    with tabs[0]:
        record_form(module, statuses, f"new_{module}")
    rows = fetch_records(module)
    with tabs[1]:
        if not rows:
            st.info("Aucun enregistrement pour ce module.")
        else:
            df = pd.DataFrame(rows)
            q = st.text_input("Rechercher dans ce module", key=f"search_{module}")
            if q:
                mask = df.astype(str).apply(lambda col: col.str.contains(q, case=False, na=False)).any(axis=1)
                df = df[mask]
            st.dataframe(df[["id","reference","title","event_date","status","priority","assigned_to","due_date"]], use_container_width=True, hide_index=True)
            ids = [int(r["id"]) for r in rows]
            chosen = st.selectbox("Choisir un enregistrement à modifier", ids, format_func=lambda rid: f"#{rid} — {next((r['title'] for r in rows if r['id']==rid), '')}", key=f"edit_select_{module}")
            existing = next(r for r in rows if r["id"] == chosen)
            with st.expander("✏️ Modifier cet enregistrement", expanded=False):
                record_form(module, statuses, f"edit_{module}_{chosen}", existing)
            with st.expander("🗑️ Supprimer un enregistrement", expanded=False):
                st.warning("La suppression est définitive. Vérifiez votre sélection.")
                confirm = st.checkbox(f"Confirmer la suppression de #{chosen}", key=f"confirm_del_{module}_{chosen}")
                if st.button("Supprimer l'enregistrement", key=f"del_{module}_{chosen}", disabled=not confirm):
                    delete_record(chosen)
                    st.success("Enregistrement supprimé.")
                    st.rerun()
    with tabs[2]:
        export_buttons(dataframe_for_export(rows), f"{module.lower().replace(' ','_')}_export")

# ---------- App shell : navigation horizontale à deux niveaux ----------
# Les noms de pages restent identiques aux modules existants afin de préserver
# les formulaires, les exports, les données SQLite et les actions déjà en place.
NAV_GROUPS = {
    "🏠 Accueil": ["🏠 Tableau de bord", "📅 Agenda et échéances", "📄 Rapports"],
    "📁 Dossiers & suivi": ["🔎 Enquêtes", "👥 Personnes", "📝 Auditions et actes", "🧩 Questionnaires", "📂 Documents & liens"],
    "🎖️ Organisation du service": ["🎖️ Activités de service", "📋 Consignes administratives", "👨‍✈️ Encadrement", "🎒 Matériel autorisé", "📚 Formation"],
    "🛡️ Administration": ["🧾 Journal d'audit", "💾 Sauvegardes", "⚙️ Paramètres"],
}

with st.sidebar:
    st.markdown("## 🇸🇳 Sergent Ousmane Youm")
    st.caption(f"Session active : {st.session_state.get('username','')}")
    st.markdown("---")
    st.caption("La navigation principale est disponible en haut de page.")
    if st.button("🔒 Se déconnecter", use_container_width=True):
        audit("Déconnexion", "Sécurité")
        st.session_state.clear()
        st.rerun()
    st.caption("SQLite local • Version administrative")

st.markdown('<div class="hero"><div class="brand-row"><div class="brand-seal">GN<small>SÉNÉGAL</small></div><div class="brand-seal mfa">MFA<small>FORCES ARMÉES</small></div><div class="brand-identity"><div class="brand-kicker">République du Sénégal · Un Peuple – Un But – Une Foi</div><h1>SERGENT OUSMANE YOUM</h1><div class="brand-subtitle">Ministère des Forces armées · Gendarmerie nationale<br>Assistant personnel de travail • Dossiers, activités, ressources et rapports</div><div class="brand-pills"><span class="brand-pill">DOSSIERS & SUIVI</span><span class="brand-pill">ADMINISTRATION</span><span class="brand-pill">DOCUMENTS & RAPPORTS</span></div></div><div class="flag-sn" aria-label="Drapeau du Sénégal"><span class="fg"></span><span class="fy">★</span><span class="fr"></span></div></div></div>', unsafe_allow_html=True)
st.markdown('<div class="topnav-wrap"><div class="nav-caption">Navigation principale</div>', unsafe_allow_html=True)
groups = list(NAV_GROUPS.keys())
if st.session_state.get("nav_group") not in groups:
    st.session_state["nav_group"] = groups[0]
st.radio("Espaces principaux", groups, horizontal=True, key="nav_group", label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)
active_group = st.session_state["nav_group"]
subpages = NAV_GROUPS[active_group]
if st.session_state.get("nav_page") not in subpages:
    st.session_state["nav_page"] = subpages[0]
st.markdown('<div class="subnav-wrap"><div class="nav-caption" style="color:#173e6b">Sous-onglets de cet espace</div>', unsafe_allow_html=True)
st.radio("Sous-onglets", subpages, horizontal=True, key="nav_page", label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)
menu = st.session_state["nav_page"]

if menu == "🏠 Tableau de bord":
    all_rows = fetch_records()
    total = len(all_rows)
    active = sum(1 for r in all_rows if r["status"] in ("En cours","Nouveau","À traiter","À faire","Programmée","À programmer"))
    closed = sum(1 for r in all_rows if r["status"] in ("Clôturé","Finalisé","Transmis","Réalisée","Réalisé","Terminée","Exécutée"))
    today = date.today().isoformat()
    overdue = sum(1 for r in all_rows if r.get("due_date") and r["due_date"] < today and r["status"] not in ("Clôturé","Finalisé","Transmis","Réalisée","Réalisé","Terminée","Exécutée","Annulée"))
    people_count = len(fetch_people())
    docs_count = len(fetch_documents())
    cols = st.columns(4)
    metrics = [("📁 Enregistrements", total), ("🔄 En cours / à traiter", active), ("✅ Terminés / transmis", closed), ("⏰ En retard", overdue)]
    for col, (label, value) in zip(cols, metrics):
        col.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div></div>', unsafe_allow_html=True)
    st.write("")
    c1, c2 = st.columns([1.3,1])
    with c1:
        st.markdown("### Activité récente")
        if all_rows:
            recent = pd.DataFrame(all_rows).sort_values("updated_at", ascending=False).head(8)
            st.dataframe(recent[["module","reference","title","status","updated_at"]], use_container_width=True, hide_index=True)
        else:
            st.info("Commencez par créer un enregistrement dans le module Enquêtes ou Activités de service.")
    with c2:
        st.markdown("### Aperçu des ressources")
        st.metric("Personnes enregistrées", people_count)
        st.metric("Documents référencés", docs_count)
        st.metric("Date du jour", date.today().strftime("%d/%m/%Y"))
    st.markdown("### Accès rapide")
    q1, q2, q3 = st.columns(3)
    q1.info("🔎 **Enquêtes**\n\nCréer et suivre un dossier administratif.")
    q2.info("🎖️ **Activités de service**\n\nConsigner les tâches et résultats.")
    q3.info("📈 **Rapports**\n\nPréparer des bilans et exporter les données.")

elif menu == "🧩 Questionnaires":
    st.markdown('<div class="section-head">Questionnaires préparés, à définir ou à compléter</div>', unsafe_allow_html=True)
    st.caption("Outil de suivi administratif et de formation. Ne saisissez pas de données opérationnelles, judiciaires ou personnelles sensibles sans autorisation et environnement sécurisé.")
    templates = {
        "Préparation d’une enquête administrative": [
            ("Objet / thème", "text"), ("Objectif de la démarche", "textarea"), ("Périmètre et période concernés", "text"),
            ("Sources ou documents à consulter (liens)", "textarea"), ("Services à consulter (sans données sensibles)", "textarea"),
            ("Questions à vérifier", "textarea"), ("Méthode de collecte prévue", "select:Entretien;Observation;Revue documentaire;Questionnaire;Autre"),
            ("Responsable du suivi", "text"), ("Échéance", "date"), ("Points restant à définir", "textarea")],
        "Préparation d’une audition ou d’un entretien": [
            ("Objet général de l’entretien", "text"), ("Date prévue", "date"), ("Lieu ou modalité", "text"),
            ("Thèmes à aborder", "textarea"), ("Questions ouvertes à préparer", "textarea"),
            ("Documents de référence (liens)", "textarea"), ("Mesures organisationnelles à prévoir", "textarea"),
            ("Statut de préparation", "select:À préparer;Prêt;Reporté;Terminé"), ("Observations administratives", "textarea")],
        "Bilan d’activité de service": [
            ("Service / unité", "text"), ("Période couverte", "text"), ("Objectifs prévus", "textarea"),
            ("Activités réalisées", "textarea"), ("Résultats observables", "textarea"), ("Difficultés rencontrées", "textarea"),
            ("Solutions proposées", "textarea"), ("Besoins / moyens à prévoir", "textarea"),
            ("Actions de suivi et échéances", "textarea"), ("Liens vers les pièces de référence", "textarea")],
        "Évaluation d’une formation": [
            ("Intitulé de la formation", "text"), ("Date / période", "text"), ("Objectifs pédagogiques", "textarea"),
            ("Contenu traité", "textarea"), ("Niveau de satisfaction", "select:Très satisfaisant;Satisfaisant;Moyen;Insuffisant;À évaluer"),
            ("Compétences acquises", "textarea"), ("Points à améliorer", "textarea"), ("Besoins complémentaires", "textarea"),
            ("Ressources utiles (liens)", "textarea")],
        "Questionnaire personnalisé — à définir": [
            ("Thème du questionnaire", "text"), ("Objectif", "textarea"), ("Public concerné (catégorie générale)", "text"),
            ("Question 1", "text"), ("Question 2", "text"), ("Question 3", "text"),
            ("Question 4", "text"), ("Question 5", "text"), ("Réponses / observations", "textarea"),
            ("Éléments restant à compléter", "textarea")]
    }
    t_create, t_fill, t_manage = st.tabs(["➕ Créer / préparer", "✍️ Compléter", "📋 Registre et exports"])
    with t_create:
        chosen_template = st.selectbox("Modèle de départ", list(templates.keys()))
        with st.form("questionnaire_create"):
            qtitle = st.text_input("Titre du questionnaire *", value=chosen_template)
            qmodule = st.selectbox("Domaine", ["Enquêtes", "Auditions et actes", "Activités de service", "Agenda et échéances", "Consignes administratives", "Encadrement", "Matériel", "Formation", "Rapports", "Autre"])
            qdesc = st.text_area("Consignes / objectif", value="À vérifier et compléter avant utilisation.")
            raw_questions = st.text_area("Questions — une par ligne au format libellé|type",
                value="\n".join(f"{a}|{b}" for a,b in templates[chosen_template]), height=260,
                help="Types acceptés : text, textarea, date, select:Option 1;Option 2.")
            create_q = st.form_submit_button("Enregistrer le questionnaire", type="primary")
        if create_q:
            questions = []
            for line in raw_questions.splitlines():
                if "|" not in line:
                    continue
                label, kind = line.split("|", 1)
                label, kind = label.strip(), kind.strip()
                if label and (kind in ("text","textarea","date") or kind.startswith("select:")):
                    questions.append({"label": label, "type": kind})
            if not qtitle.strip():
                st.error("Le titre est obligatoire.")
            elif not questions:
                st.error("Ajoutez au moins une question valide.")
            else:
                stamp = now_iso()
                with connect() as con:
                    cur = con.execute("INSERT INTO questionnaires(title,module,description,questions_json,status,created_at,updated_at) VALUES(?,?,?,?,?,?,?)",
                        (qtitle.strip(), qmodule, qdesc.strip(), json.dumps(questions, ensure_ascii=False), "À compléter", stamp, stamp))
                    con.commit()
                    qid = cur.lastrowid
                audit("Création questionnaire", qmodule, qid, qtitle)
                st.success("Questionnaire enregistré.")
                st.rerun()
    with connect() as con:
        questionnaires = [dict(r) for r in con.execute("SELECT * FROM questionnaires ORDER BY updated_at DESC,id DESC").fetchall()]
    with t_fill:
        if not questionnaires:
            st.info("Créez d’abord un questionnaire dans l’onglet « Créer / préparer ».")
        else:
            selected_qid = st.selectbox("Questionnaire à compléter", [q["id"] for q in questionnaires],
                format_func=lambda x: f"#{x} — {next(q['title'] for q in questionnaires if q['id']==x)}")
            q = next(q for q in questionnaires if q["id"] == selected_qid)
            st.write(q["description"])
            questions = json.loads(q["questions_json"])
            with st.form(f"answer_questionnaire_{selected_qid}"):
                respondent = st.text_input("Nom / fonction du répondant (facultatif)")
                answers = {}
                for i, item in enumerate(questions):
                    label, kind = item["label"], item["type"]
                    key = f"answer_{selected_qid}_{i}"
                    if kind == "textarea":
                        answers[label] = st.text_area(label, key=key)
                    elif kind == "date":
                        answers[label] = st.date_input(label, key=key).isoformat()
                    elif kind.startswith("select:"):
                        opts = [x.strip() for x in kind[7:].split(";") if x.strip()]
                        answers[label] = st.selectbox(label, opts or ["À définir"], key=key)
                    else:
                        answers[label] = st.text_input(label, key=key)
                answer_notes = st.text_area("Observations complémentaires")
                save_answers = st.form_submit_button("Enregistrer les réponses", type="primary")
            if save_answers:
                with connect() as con:
                    con.execute("INSERT INTO questionnaire_responses(questionnaire_id,respondent,answers_json,notes,completed_at) VALUES(?,?,?,?,?)",
                        (selected_qid, respondent.strip(), json.dumps(answers, ensure_ascii=False), answer_notes.strip(), now_iso()))
                    con.execute("UPDATE questionnaires SET status=?,updated_at=? WHERE id=?",
                        ("Complété" if all(str(v).strip() for v in answers.values()) else "En cours", now_iso(), selected_qid))
                    con.commit()
                audit("Réponses questionnaire enregistrées", q["module"], selected_qid, q["title"])
                st.success("Réponses enregistrées.")
                st.rerun()
    with t_manage:
        if questionnaires:
            qdf = pd.DataFrame([{k:q.get(k,"") for k in ["id","title","module","description","status","created_at","updated_at"]} for q in questionnaires])
            st.dataframe(qdf, use_container_width=True, hide_index=True)
            qid = st.selectbox("Questionnaire à gérer / exporter", [q["id"] for q in questionnaires], key="manage_qid",
                format_func=lambda x: f"#{x} — {next(q['title'] for q in questionnaires if q['id']==x)}")
            q = next(q for q in questionnaires if q["id"] == qid)
            with connect() as con:
                response_rows = [dict(r) for r in con.execute("SELECT * FROM questionnaire_responses WHERE questionnaire_id=? ORDER BY id DESC", (qid,)).fetchall()]
            if response_rows:
                flattened = []
                for rr in response_rows:
                    row = {"id":rr["id"],"questionnaire":q["title"],"répondant":rr["respondent"],"date":rr["completed_at"],"observations":rr["notes"]}
                    row.update(json.loads(rr["answers_json"]))
                    flattened.append(row)
                export_buttons(pd.DataFrame(flattened), f"questionnaire_{qid}_reponses")
                st.dataframe(pd.DataFrame(flattened), use_container_width=True, hide_index=True)
            else:
                st.info("Aucune réponse enregistrée pour ce questionnaire.")
            with st.expander("Supprimer le questionnaire et ses réponses"):
                confirm_qdel = st.checkbox("Confirmer la suppression définitive", key=f"qdel_{qid}")
                if st.button("Supprimer ce questionnaire", disabled=not confirm_qdel, key=f"delete_q_{qid}"):
                    with connect() as con:
                        con.execute("DELETE FROM questionnaire_responses WHERE questionnaire_id=?", (qid,))
                        con.execute("DELETE FROM questionnaires WHERE id=?", (qid,))
                        con.commit()
                    audit("Suppression questionnaire", q["module"], qid, q["title"])
                    st.rerun()
        else:
            st.info("Aucun questionnaire à afficher.")

elif menu == "👥 Personnes":
    st.markdown('<div class="section-head">Registre des personnes associées aux dossiers</div>', unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["➕ Ajouter", "📋 Registre", "📤 Exports"])
    with t1:
        with st.form("person_add"):
            full_name = st.text_input("Nom et prénom *")
            role = st.selectbox("Qualité / rôle déclaré", ["À préciser", "Plaignant", "Témoin", "Victime présumée", "Personne entendue", "Autre"])
            contact = st.text_input("Coordonnées nécessaires au suivi (facultatif)")
            linked_reference = st.text_input("Référence du dossier associé")
            notes = st.text_area("Notes factuelles et pertinentes")
            submitted = st.form_submit_button("Enregistrer la personne", type="primary")
        if submitted:
            if not full_name.strip():
                st.error("Le nom est obligatoire.")
            else:
                with connect() as con:
                    cur = con.execute("INSERT INTO people(full_name,role,contact,linked_reference,notes,created_at) VALUES(?,?,?,?,?,?)",
                                       (full_name.strip(), role, contact.strip(), linked_reference.strip(), notes.strip(), now_iso()))
                    con.commit()
                    pid = cur.lastrowid
                audit("Création", "Personnes", pid, full_name)
                st.success("Personne enregistrée.")
                st.rerun()
    people = fetch_people()
    with t2:
        if people:
            pdf = pd.DataFrame(people)
            query = st.text_input("Rechercher une personne")
            if query:
                pdf = pdf[pdf.astype(str).apply(lambda c: c.str.contains(query, case=False, na=False)).any(axis=1)]
            st.dataframe(pdf, use_container_width=True, hide_index=True)
            if people:
                ids = [p["id"] for p in people]
                pid = st.selectbox("Sélectionner une fiche à modifier", ids, format_func=lambda x: f"#{x} — {next((p['full_name'] for p in people if p['id']==x),'')}")
                person = next(p for p in people if p["id"] == pid)
                with st.expander("Modifier la fiche"):
                    with st.form(f"person_edit_{pid}"):
                        nm = st.text_input("Nom et prénom", value=person["full_name"])
                        rl = st.selectbox("Qualité / rôle", ["À préciser", "Plaignant", "Témoin", "Victime présumée", "Personne entendue", "Autre"], index=(["À préciser", "Plaignant", "Témoin", "Victime présumée", "Personne entendue", "Autre"].index(person["role"]) if person["role"] in ["À préciser", "Plaignant", "Témoin", "Victime présumée", "Personne entendue", "Autre"] else 0))
                        ct = st.text_input("Coordonnées", value=person["contact"] or "")
                        lr = st.text_input("Référence associée", value=person["linked_reference"] or "")
                        nt = st.text_area("Notes", value=person["notes"] or "")
                        savep = st.form_submit_button("Enregistrer les modifications")
                    if savep:
                        with connect() as con:
                            con.execute("UPDATE people SET full_name=?,role=?,contact=?,linked_reference=?,notes=? WHERE id=?",(nm.strip(),rl,ct.strip(),lr.strip(),nt.strip(),pid))
                            con.commit()
                        audit("Modification","Personnes",pid,nm)
                        st.rerun()
                with st.expander("Supprimer une fiche"):
                    confp = st.checkbox(f"Confirmer la suppression de {person['full_name']}", key=f"delperson{pid}")
                    if st.button("Supprimer cette personne", disabled=not confp):
                        with connect() as con:
                            con.execute("DELETE FROM people WHERE id=?", (pid,))
                            con.commit()
                        audit("Suppression","Personnes",pid,person["full_name"])
                        st.rerun()
        else:
            st.info("Aucune personne enregistrée.")
    with t3:
        export_buttons(dataframe_for_export(people), "personnes")

elif menu == "📂 Documents & liens":
    st.markdown('<div class="section-head">Centre documentaire — priorité aux liens</div>', unsafe_allow_html=True)
    st.caption("Ajoutez d’abord un lien vers une ressource existante. Le dépôt de fichier reste facultatif afin de limiter l’espace utilisé.")
    with st.form("document_add"):
        title = st.text_input("Titre de la ressource *")
        category = st.selectbox("Catégorie", ["Rapport", "Compte rendu", "Document administratif", "Formulaire / questionnaire", "Guide / procédure", "Courrier reçu", "Courrier envoyé", "Autre"])
        linked_reference = st.text_input("Référence associée (facultatif)")
        url = st.text_input("Lien URL (prioritaire)", placeholder="https://...")
        description = st.text_area("Description / utilité")
        uploaded = st.file_uploader("Ou joindre un fichier (facultatif)", type=["pdf","doc","docx","xls","xlsx"])
        save_doc = st.form_submit_button("Enregistrer la ressource", type="primary")
    if save_doc:
        valid_url = (not url.strip()) or bool(re.match(r"^https?://\S+$", url.strip(), re.I))
        if not title.strip():
            st.error("Le titre est obligatoire.")
        elif not valid_url:
            st.error("Le lien doit commencer par http:// ou https://.")
        elif not url.strip() and uploaded is None:
            st.error("Ajoutez un lien ou joignez un fichier.")
        else:
            file_name = ""
            file_path = ""
            if uploaded is not None:
                safe_name = Path(uploaded.name).name.replace(" ", "_")
                unique_name = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{secrets.token_hex(4)}_{safe_name}"
                target = UPLOAD_DIR / unique_name
                target.write_bytes(uploaded.getvalue())
                file_name, file_path = uploaded.name, str(target.relative_to(APP_DIR))
            with connect() as con:
                cur = con.execute("""INSERT INTO documents(title,category,linked_reference,file_name,file_path,description,url,created_at)
                    VALUES(?,?,?,?,?,?,?,?)""",
                    (title.strip(), category, linked_reference.strip(), file_name, file_path, description.strip(), url.strip(), now_iso()))
                con.commit()
                did = cur.lastrowid
            audit("Ajout de ressource", "Documents", did, title)
            st.success("Ressource enregistrée.")
            st.rerun()
    docs = fetch_documents()
    if docs:
        st.markdown("### Ressources enregistrées")
        ddf = pd.DataFrame(docs)
        cols = [c for c in ["id","title","category","linked_reference","url","file_name","description","created_at"] if c in ddf.columns]
        st.dataframe(ddf[cols], use_container_width=True, hide_index=True)
        did = st.selectbox("Choisir une ressource", [d["id"] for d in docs], format_func=lambda x: f"#{x} — {next((d['title'] for d in docs if d['id']==x),'')}")
        docrow = next(d for d in docs if d["id"] == did)
        if docrow.get("url"):
            st.link_button("🔗 Ouvrir la ressource en ligne", docrow["url"], use_container_width=True)
        path_text = docrow.get("file_path") or ""
        path = APP_DIR / path_text if path_text else None
        if path and path.exists():
            st.download_button("⬇️ Télécharger le fichier joint", path.read_bytes(), docrow.get("file_name") or path.name, use_container_width=True)
        elif docrow.get("file_name"):
            st.warning("Le fichier joint est introuvable. Le lien, s’il existe, reste disponible.")
        with st.expander("Supprimer la ressource sélectionnée"):
            confd = st.checkbox("Confirmer la suppression", key=f"docdel{did}")
            if st.button("Supprimer la ressource", disabled=not confd):
                try:
                    if path and path.exists():
                        path.unlink()
                except Exception:
                    pass
                with connect() as con:
                    con.execute("DELETE FROM documents WHERE id=?", (did,))
                    con.commit()
                audit("Suppression", "Documents", did, docrow.get("title",""))
                st.rerun()
        export_buttons(dataframe_for_export(docs), "documents_liens")
    else:
        st.info("Aucune ressource enregistrée pour le moment.")

elif menu in [label for label in MODULES if label in ["📝 Auditions et actes","📅 Agenda et échéances","🎖️ Activités de service","👨‍✈️ Encadrement","🎒 Matériel autorisé","📚 Formation","📋 Consignes administratives","📄 Rapports","🔎 Enquêtes"]]:
    module, statuses = MODULES[menu]
    show_records_module(menu, module, statuses)

elif menu == "🧾 Journal d'audit":
    st.markdown('<div class="section-head">Journal des opérations</div>', unsafe_allow_html=True)
    with connect() as con:
        logs = [dict(r) for r in con.execute("SELECT * FROM audit_log ORDER BY id DESC LIMIT 1000").fetchall()]
    if logs:
        st.dataframe(pd.DataFrame(logs), use_container_width=True, hide_index=True)
        export_buttons(pd.DataFrame(logs), "journal_audit")
    else:
        st.info("Aucune opération journalisée.")

elif menu == "💾 Sauvegardes":
    st.markdown('<div class="section-head">Sauvegarde des données PostgreSQL</div>', unsafe_allow_html=True)
    st.info("Les données sont enregistrées dans Supabase PostgreSQL. Pour une sauvegarde de travail, vous pouvez télécharger les tables au format Excel. Les sauvegardes natives et restaurations complètes se gèrent depuis le tableau de bord Supabase.")
    if st.button("Préparer la sauvegarde Excel", type="primary"):
        try:
            tables = ["settings", "records", "people", "documents", "questionnaires", "questionnaire_responses", "audit_log"]
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                with connect() as con:
                    for table in tables:
                        rows = con.execute(f"SELECT * FROM {table} ORDER BY id" if table != "settings" else "SELECT * FROM settings ORDER BY key").fetchall()
                        df_table = pd.DataFrame([dict(row) for row in rows])
                        if df_table.empty:
                            df_table = pd.DataFrame(columns=["Aucune donnée"])
                        df_table.to_excel(writer, index=False, sheet_name=table[:31])
            st.download_button("📊 Télécharger la sauvegarde Excel", output.getvalue(), f"sergent_ousmane_you m_sauvegarde_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx".replace(" ", ""), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", type="primary")
            audit("Sauvegarde Excel préparée", "Sauvegardes")
        except Exception as exc:
            st.error(f"Impossible de préparer la sauvegarde : {exc}")
    st.markdown("### Bonnes pratiques")
    st.markdown("- Activez les sauvegardes automatiques depuis le tableau de bord Supabase.\n- Ne partagez jamais la chaîne de connexion ni le mot de passe.\n- Pour restaurer toute la base, utilisez une sauvegarde native PostgreSQL depuis un environnement administrateur autorisé.")

elif menu == "⚙️ Paramètres":
    st.markdown('<div class="section-head">Paramètres et sécurité</div>', unsafe_allow_html=True)
    st.markdown("### Changer le mot de passe")
    with st.form("change_password"):
        current = st.text_input("Mot de passe actuel", type="password")
        new1 = st.text_input("Nouveau mot de passe (12 caractères minimum)", type="password")
        new2 = st.text_input("Confirmer le nouveau mot de passe", type="password")
        change = st.form_submit_button("Mettre à jour le mot de passe", type="primary")
    if change:
        encoded = get_setting("password_hash", "")
        if not verify_password(current, encoded):
            st.error("Le mot de passe actuel est incorrect.")
        elif len(new1) < 12:
            st.error("Le nouveau mot de passe doit contenir au moins 12 caractères.")
        elif new1 != new2:
            st.error("Les nouveaux mots de passe ne correspondent pas.")
        else:
            set_setting("password_hash", hash_password(new1))
            audit("Changement de mot de passe", "Sécurité")
            st.success("Mot de passe mis à jour.")
    st.markdown("### État du stockage")
    st.write("Base de données : Supabase PostgreSQL (connexion SSL obligatoire)")
    st.write(f"Dossier local des pièces jointes : `{UPLOAD_DIR}`")
    st.caption("Les données métier sont stockées dans PostgreSQL. Les fichiers joints restent sur le disque local de l’application ; pour un déploiement cloud durable, utilisez Supabase Storage ou un stockage objet persistant.")
    st.markdown("### Réinitialisation")
    st.warning("Cette action supprime les données de travail. Faites d'abord une sauvegarde.")
    if st.button("Afficher les instructions de réinitialisation"):
        st.code("1. Ouvrir le tableau de bord Supabase.\n2. Vérifier les sauvegardes PostgreSQL.\n3. Ne jamais publier les secrets de connexion.\n4. Pour supprimer des données, utiliser une procédure validée et sauvegarder avant toute opération.")

st.markdown("""
<div class="footer-panel">
  <div class="footer-grid">
    <div>
      <h3>🇸🇳 SERGENT OUSMANE YOUM</h3>
      <p><strong>Un espace de travail numérique organisé, clair et centralisé.</strong></p>
      <p>Sergent Ousmane Youm est un assistant personnel de travail qui rassemble dans une interface unique le suivi des dossiers, les questionnaires, les personnes associées, les actes, l'agenda, les activités de service, les consignes, les formations, les ressources documentaires et les rapports. Son objectif est de faciliter l'organisation du travail, la traçabilité des opérations administratives et la consultation des informations utiles.</p>
      <p>La navigation par espaces et sous-onglets permet d'accéder plus rapidement aux fonctionnalités, tandis que les registres, exports et sauvegardes aident à structurer et conserver le travail effectué.</p>
    </div>
    <div>
      <h3>Principes de la plateforme</h3>
      <p>• Organisation par modules<br>• Suivi des enregistrements et échéances<br>• Questionnaires prédéfinis ou personnalisables<br>• Référencement de ressources par liens<br>• Exports PDF, Word et Excel<br>• Journalisation de certaines actions</p>
    </div>
  </div>
  <div class="footer-bottom">Sergent Ousmane Youm • Assistant personnel de travail • Exports PDF / Word / Excel • Version Supabase PostgreSQL.<br>Outil à utiliser uniquement dans un cadre autorisé. Avant toute utilisation réelle, vérifier les règles de sécurité, les droits d'accès, la protection des données et les exigences applicables à l'hébergement.</div>
</div>
""", unsafe_allow_html=True)
