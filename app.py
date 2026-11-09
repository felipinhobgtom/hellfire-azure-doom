from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

ROOT = Path(__file__).resolve().parent
DB_PATH = Path(os.environ.get("DATABASE_PATH", ROOT / "data" / "doom.db"))
app = Flask(__name__, static_folder="web", static_url_path="")


def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB_PATH, timeout=10)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("""CREATE TABLE IF NOT EXISTS scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        player TEXT NOT NULL CHECK(length(player) BETWEEN 1 AND 24),
        kills INTEGER NOT NULL CHECK(kills BETWEEN 0 AND 999999),
        created_at TEXT NOT NULL
    )""")
    return db


@app.get("/api/health")
def health():
    with connect() as db:
        db.execute("SELECT 1")
    return jsonify(status="ok", database="sqlite")


@app.get("/api/scores")
def scores():
    with connect() as db:
        rows = db.execute("SELECT id, player, kills, created_at FROM scores ORDER BY kills DESC, id ASC LIMIT 10").fetchall()
    return jsonify([dict(row) for row in rows])


@app.post("/api/scores")
def add_score():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify(error="Envie um objeto JSON."), 400
    player = payload.get("player")
    kills = payload.get("kills")
    if not isinstance(player, str) or not player.strip() or len(player.strip()) > 24:
        return jsonify(error="player deve ter de 1 a 24 caracteres."), 400
    if isinstance(kills, bool) or not isinstance(kills, int) or not 0 <= kills <= 999999:
        return jsonify(error="kills deve ser um inteiro entre 0 e 999999."), 400
    created = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with connect() as db:
        cursor = db.execute("INSERT INTO scores(player, kills, created_at) VALUES (?, ?, ?)", (player.strip(), kills, created))
        result = db.execute("SELECT id, player, kills, created_at FROM scores WHERE id=?", (cursor.lastrowid,)).fetchone()
    return jsonify(dict(result)), 201


@app.get("/")
def index():
    return send_from_directory(ROOT / "web", "index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))
