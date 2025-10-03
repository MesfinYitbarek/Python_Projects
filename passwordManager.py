import sqlite3
import os
import base64
import getpass
import datetime
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend

DB_FILE = "vault.db"
KDF_ITERATIONS = 390000  # strong iteration count


def init_db():
    """Create DB and tables if not exist. Store a random salt in meta table on first run."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS meta (
            id INTEGER PRIMARY KEY CHECK(id=1),
            salt BLOB,
            kdf_iterations INTEGER
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            username TEXT,
            password BLOB NOT NULL,
            notes TEXT,
            created_at TEXT NOT NULL
        )
        """
    )
    # Ensure single-row meta exists
    c.execute("SELECT salt FROM meta WHERE id = 1")
    row = c.fetchone()
    if row is None:
        salt = os.urandom(16)
        c.execute(
            "INSERT INTO meta (id, salt, kdf_iterations) VALUES (1, ?, ?)",
            (salt, KDF_ITERATIONS),
        )
        conn.commit()
    conn.close()


def get_meta():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT salt, kdf_iterations FROM meta WHERE id = 1")
    row = c.fetchone()
    conn.close()
    if not row:
        raise RuntimeError("Database meta not initialized.")
    return row[0], row[1]


def derive_key(master_password: str, salt: bytes, iterations: int) -> bytes:
    """Derive a 32-byte key from master_password using PBKDF2-HMAC-SHA256."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(), length=32, salt=salt, iterations=iterations, backend=default_backend()
    )
    key = kdf.derive(master_password.encode("utf-8"))
    return base64.urlsafe_b64encode(key)  # Fernet expects a urlsafe base64-encoded key


def open_vault(master_password: str):
    salt, iterations = get_meta()
    key = derive_key(master_password, salt, iterations)
    return Fernet(key)


def add_entry(f: Fernet, name: str, username: str, password_plain: str, notes: str = ""):
    token = f.encrypt(password_plain.encode("utf-8"))
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "INSERT INTO entries (name, username, password, notes, created_at) VALUES (?, ?, ?, ?, ?)",
        (name, username, token, notes, datetime.datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()
    print(f"Entry '{name}' saved.")


def get_entry(f: Fernet, entry_id: int):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, name, username, password, notes, created_at FROM entries WHERE id = ?", (entry_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        print("Entry not found.")
        return
    try:
        decrypted = f.decrypt(row[3]).decode("utf-8")
    except Exception as e:
        print("Decryption failed — wrong master password or corrupted data.")
        return
    print("----- Entry -----")
    print(f"ID: {row[0]}")
    print(f"Name: {row[1]}")
    print(f"Username: {row[2]}")
    print(f"Password: {decrypted}")
    print(f"Notes: {row[4]}")
    print(f"Created (UTC): {row[5]}")
    print("-----------------")


def list_entries():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, name, username, created_at FROM entries ORDER BY id")
    rows = c.fetchall()
    conn.close()
    if not rows:
        print("No entries yet.")
        return
    print("ID | Name | Username | Created (UTC)")
    print("-" * 40)
    for r in rows:
        print(f"{r[0]:<3} {r[1]:<20} {r[2] or '-':<15} {r[3]}")


def delete_entry(entry_id: int):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
    conn.commit()
    changed = c.rowcount
    conn.close()
    if changed:
        print(f"Entry {entry_id} deleted.")
    else:
        print("Entry not found.")


def interactive_menu():
    print("Simple Password Manager — local vault")
    init_db()
    master = getpass.getpass("Enter master password: ")
    # open vasult
    try:
        f = open_vault(master)
    except Exception as e:
        print("Failed to open vault:", e)
        return

    while True:
        print("\nChoose an action:")
        print("1) Add entry")
        print("2) Get entry (by id)")
        print("3) List entries")
        print("4) Delete entry (by id)")
        print("5) Quit")
        choice = input("> ").strip()
        if choice == "1":
            name = input("Name (e.g. 'Gmail'): ").strip()
            username = input("Username/email (optional): ").strip()
            pwd = getpass.getpass("Password (will not be shown): ")
            notes = input("Notes (optional): ").strip()
            add_entry(f, name, username, pwd, notes)
        elif choice == "2":
            try:
                entry_id = int(input("Entry ID: ").strip())
            except ValueError:
                print("Invalid id.")
                continue
            get_entry(f, entry_id)
        elif choice == "3":
            list_entries()
        elif choice == "4":
            try:
                entry_id = int(input("Entry ID to delete: ").strip())
            except ValueError:
                print("Invalid id.")
                continue
            confirm = input(f"Delete entry {entry_id}? [y/N]: ").lower()
            if confirm == "y":
                delete_entry(entry_id)
            else:
                print("Cancelled.")
        elif choice == "5":
            print("Goodbye.")
            break
        else:
            print("Unknown option.")


if __name__ == "__main__":
    interactive_menu()
