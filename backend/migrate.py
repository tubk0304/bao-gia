import sqlite3

def migrate():
    conn = sqlite3.connect('catalog.db')
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE products ADD COLUMN details VARCHAR DEFAULT ''")
        print("Migrated successfully.")
    except sqlite3.OperationalError as e:
        print(f"Migration error or already applied: {e}")
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    migrate()
