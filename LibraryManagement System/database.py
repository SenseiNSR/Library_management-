import sqlite3
import os

DB_FILE = 'library.db'

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create Books table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            isbn TEXT UNIQUE,
            status TEXT DEFAULT 'Available'
        )
    ''')
    
    # Create Members table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT
        )
    ''')
    
    # Create Transactions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER,
            member_id INTEGER,
            issue_date DATE DEFAULT (date('now')),
            return_date DATE,
            FOREIGN KEY(book_id) REFERENCES books(id),
            FOREIGN KEY(member_id) REFERENCES members(id)
        )
    ''')
    
    # Insert sample data if empty
    cursor.execute('SELECT COUNT(*) FROM books')
    if cursor.fetchone()[0] == 0:
        sample_books = [
            ('The Great Gatsby', 'F. Scott Fitzgerald', '978-0743273565'),
            ('1984', 'George Orwell', '978-0451524935'),
            ('To Kill a Mockingbird', 'Harper Lee', '978-0060935467'),
            ('Pride and Prejudice', 'Jane Austen', '978-0141439518')
        ]
        cursor.executemany('INSERT INTO books (title, author, isbn) VALUES (?, ?, ?)', sample_books)
        
    conn.commit()
    conn.close()
