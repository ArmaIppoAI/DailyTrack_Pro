import sqlite3
from datetime import datetime
from .config import DB_PATH

def connect_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("""
    CREATE TABLE IF NOT EXISTS daily (
        day TEXT PRIMARY KEY,
        water_ml INTEGER NOT NULL DEFAULT 0,
        steps INTEGER NOT NULL DEFAULT 0,
        note TEXT NOT NULL DEFAULT '',
        weight_kg REAL,
        updated_at TEXT NOT NULL
    )""")
    conn.execute("""
    CREATE TABLE IF NOT EXISTS meals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        day TEXT NOT NULL,
        name TEXT NOT NULL,
        quantity_g REAL NOT NULL,
        calories REAL NOT NULL DEFAULT 0,
        protein_g REAL NOT NULL DEFAULT 0,
        carbs_g REAL NOT NULL DEFAULT 0,
        fat_g REAL NOT NULL DEFAULT 0,
        source TEXT NOT NULL DEFAULT 'manual',
        created_at TEXT NOT NULL
    )""")
    conn.execute("""
    CREATE TABLE IF NOT EXISTS workouts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        day TEXT NOT NULL,
        kind TEXT NOT NULL DEFAULT 'Camminata',
        started_at TEXT NOT NULL,
        ended_at TEXT,
        duration_seconds INTEGER NOT NULL DEFAULT 0,
        steps INTEGER NOT NULL DEFAULT 0,
        distance_km REAL NOT NULL DEFAULT 0
    )""")
    # Migrazione semplice per database creati da versioni precedenti
    columns = {r["name"] for r in conn.execute("PRAGMA table_info(daily)").fetchall()}
    if "weight_kg" not in columns:
        conn.execute("ALTER TABLE daily ADD COLUMN weight_kg REAL")
    conn.commit()
    return conn

def ensure_day(conn, day):
    conn.execute(
        "INSERT OR IGNORE INTO daily(day, updated_at) VALUES (?, ?)",
        (day, datetime.now().isoformat(timespec="seconds")))
    conn.commit()

def get_day(conn, day):
    ensure_day(conn, day)
    return conn.execute("SELECT * FROM daily WHERE day=?", (day,)).fetchone()

def save_day(conn, day, water_ml=None, steps=None, note=None, weight_kg=None):
    row = get_day(conn, day)
    water = row["water_ml"] if water_ml is None else max(0, int(water_ml))
    step_count = row["steps"] if steps is None else max(0, int(steps))
    note_text = row["note"] if note is None else note
    weight = row["weight_kg"] if weight_kg is None else max(0.1, float(weight_kg))
    conn.execute("""UPDATE daily SET water_ml=?, steps=?, note=?, weight_kg=?, updated_at=? WHERE day=?""",
        (water, step_count, note_text, weight, datetime.now().isoformat(timespec="seconds"), day))
    conn.commit()

def add_meal(conn, day, name, quantity_g, calories, protein_g, carbs_g, fat_g, source="manual"):
    conn.execute("""INSERT INTO meals(day,name,quantity_g,calories,protein_g,carbs_g,fat_g,source,created_at)
        VALUES(?,?,?,?,?,?,?,?,?)""",
        (day, name, float(quantity_g), float(calories), float(protein_g), float(carbs_g),
         float(fat_g), source, datetime.now().isoformat(timespec="seconds")))
    conn.commit()

def delete_meal(conn, meal_id):
    conn.execute("DELETE FROM meals WHERE id=?", (meal_id,))
    conn.commit()

def meals_for_day(conn, day):
    return conn.execute("SELECT * FROM meals WHERE day=? ORDER BY id DESC", (day,)).fetchall()

def nutrition_totals(conn, day):
    row = conn.execute("""SELECT COALESCE(SUM(calories),0) calories,
        COALESCE(SUM(protein_g),0) protein_g, COALESCE(SUM(carbs_g),0) carbs_g,
        COALESCE(SUM(fat_g),0) fat_g FROM meals WHERE day=?""", (day,)).fetchone()
    return row

def add_workout(conn, day, started_at, ended_at, duration_seconds, steps, distance_km):
    conn.execute("""INSERT INTO workouts(day,kind,started_at,ended_at,duration_seconds,steps,distance_km)
        VALUES(?,?,?,?,?,?,?)""",
        (day, "Camminata", started_at, ended_at, int(duration_seconds), int(steps), float(distance_km)))
    conn.commit()
    if steps > 0:
        current = get_day(conn, day)
        save_day(conn, day, steps=current["steps"] + int(steps))

def workouts_for_day(conn, day):
    return conn.execute("SELECT * FROM workouts WHERE day=? ORDER BY id DESC", (day,)).fetchall()

def recent_days(conn, limit=90):
    return conn.execute("""SELECT d.*,
        (SELECT COALESCE(SUM(calories),0) FROM meals m WHERE m.day=d.day) calories,
        (SELECT COALESCE(SUM(protein_g),0) FROM meals m WHERE m.day=d.day) protein_g
        FROM daily d ORDER BY d.day DESC LIMIT ?""", (limit,)).fetchall()
