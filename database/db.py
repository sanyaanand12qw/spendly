import os
import sqlite3

from flask import g, current_app


def get_db():
    if 'db' not in g:
        db_path = current_app.config.get(
            'DATABASE',
            os.path.join(current_app.root_path, 'spendly.db'),
        )
        g.db = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row
        g.db.execute('PRAGMA foreign_keys = ON')
    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    db.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT    NOT NULL,
            email         TEXT    NOT NULL UNIQUE,
            password_hash TEXT    NOT NULL,
            created_at    TEXT    DEFAULT (datetime('now'))
        )
    ''')
    db.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL REFERENCES users(id),
            amount      REAL    NOT NULL,
            category    TEXT    NOT NULL,
            date        TEXT    NOT NULL,
            description TEXT,
            created_at  TEXT    DEFAULT (datetime('now'))
        )
    ''')
    db.commit()


def seed_db():
    from werkzeug.security import generate_password_hash

    db = get_db()
    row = db.execute('SELECT COUNT(*) FROM users').fetchone()
    if row[0] > 0:
        return

    db.execute(
        'INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)',
        ('Demo User', 'demo@spendly.com', generate_password_hash('demo123')),
    )
    db.commit()

    user = db.execute(
        'SELECT id FROM users WHERE email = ?', ('demo@spendly.com',)
    ).fetchone()
    uid = user['id']

    db.executemany(
        'INSERT INTO expenses (user_id, amount, category, date, description)'
        ' VALUES (?, ?, ?, ?, ?)',
        [
            (uid, 850.00,  'Food',          '2026-09-01', 'Weekly groceries'),
            (uid, 120.50,  'Transport',     '2026-09-02', 'Metro monthly pass'),
            (uid, 1500.00, 'Bills',         '2026-09-03', 'Electricity bill'),
            (uid, 450.00,  'Health',        '2026-09-05', 'Pharmacy'),
            (uid, 600.00,  'Entertainment', '2026-09-07', 'Cinema and dinner'),
            (uid, 2200.00, 'Shopping',      '2026-09-10', 'Clothes'),
            (uid, 300.00,  'Other',         '2026-09-12', 'Miscellaneous'),
            (uid, 950.00,  'Food',          '2026-09-15', 'Restaurant dinner'),
        ],
    )
    db.commit()
