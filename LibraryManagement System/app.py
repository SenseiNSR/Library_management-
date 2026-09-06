from flask import Flask, render_template, request, redirect, url_for, flash
import database
import sqlite3

app = Flask(__name__)
app.secret_key = 'super_secret_classy_key'

# Initialize the database when the app starts
database.init_db()

@app.route('/')
def index():
    conn = database.get_db_connection()
    
    # Get basic stats
    total_books = conn.execute('SELECT COUNT(*) FROM books').fetchone()[0]
    available_books = conn.execute("SELECT COUNT(*) FROM books WHERE status='Available'").fetchone()[0]
    total_members = conn.execute('SELECT COUNT(*) FROM members').fetchone()[0]
    
    # Get recent transactions
    recent_transactions = conn.execute('''
        SELECT t.id, b.title, m.name, t.issue_date, t.return_date 
        FROM transactions t
        JOIN books b ON t.book_id = b.id
        JOIN members m ON t.member_id = m.id
        ORDER BY t.issue_date DESC LIMIT 5
    ''').fetchall()
    
    conn.close()
    return render_template('index.html', total_books=total_books, available_books=available_books, 
                           total_members=total_members, recent_transactions=recent_transactions)

@app.route('/books')
def books():
    conn = database.get_db_connection()
    books_list = conn.execute('SELECT * FROM books').fetchall()
    conn.close()
    return render_template('books.html', books=books_list)

@app.route('/books/add', methods=('GET', 'POST'))
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        isbn = request.form['isbn']
        
        if not title or not author:
            flash('Title and Author are required!')
        else:
            conn = database.get_db_connection()
            try:
                conn.execute('INSERT INTO books (title, author, isbn) VALUES (?, ?, ?)',
                             (title, author, isbn))
                conn.commit()
                flash('Book added successfully!', 'success')
                return redirect(url_for('books'))
            except sqlite3.IntegrityError:
                flash('A book with this ISBN already exists.', 'error')
            finally:
                conn.close()
                
    return render_template('add_book.html')

@app.route('/members')
def members():
    conn = database.get_db_connection()
    members_list = conn.execute('SELECT * FROM members').fetchall()
    conn.close()
    return render_template('members.html', members=members_list)

@app.route('/members/add', methods=('GET', 'POST'))
def add_member():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        
        if not name or not email:
            flash('Name and Email are required!', 'error')
        else:
            conn = database.get_db_connection()
            try:
                conn.execute('INSERT INTO members (name, email, phone) VALUES (?, ?, ?)',
                             (name, email, phone))
                conn.commit()
                flash('Member added successfully!', 'success')
                return redirect(url_for('members'))
            except sqlite3.IntegrityError:
                flash('A member with this email already exists.', 'error')
            finally:
                conn.close()
                
    return render_template('add_member.html')

@app.route('/circulation')
def circulation():
    conn = database.get_db_connection()
    transactions = conn.execute('''
        SELECT t.id, b.title, m.name, t.issue_date, t.return_date 
        FROM transactions t
        JOIN books b ON t.book_id = b.id
        JOIN members m ON t.member_id = m.id
        ORDER BY t.issue_date DESC
    ''').fetchall()
    conn.close()
    return render_template('circulation.html', transactions=transactions)

@app.route('/circulation/issue', methods=('GET', 'POST'))
def issue_book():
    conn = database.get_db_connection()
    if request.method == 'POST':
        book_id = request.form['book_id']
        member_id = request.form['member_id']
        
        if not book_id or not member_id:
            flash('Please select both a book and a member.', 'error')
        else:
            conn.execute('INSERT INTO transactions (book_id, member_id) VALUES (?, ?)', (book_id, member_id))
            conn.execute("UPDATE books SET status = 'Issued' WHERE id = ?", (book_id,))
            conn.commit()
            flash('Book issued successfully!', 'success')
            conn.close()
            return redirect(url_for('circulation'))
            
    available_books = conn.execute("SELECT * FROM books WHERE status = 'Available'").fetchall()
    members_list = conn.execute('SELECT * FROM members').fetchall()
    conn.close()
    
    return render_template('issue_book.html', books=available_books, members=members_list)

@app.route('/circulation/return/<int:transaction_id>', methods=('POST',))
def return_book(transaction_id):
    conn = database.get_db_connection()
    transaction = conn.execute('SELECT * FROM transactions WHERE id = ?', (transaction_id,)).fetchone()
    if transaction and not transaction['return_date']:
        conn.execute("UPDATE transactions SET return_date = date('now') WHERE id = ?", (transaction_id,))
        conn.execute("UPDATE books SET status = 'Available' WHERE id = ?", (transaction['book_id'],))
        conn.commit()
        flash('Book returned successfully!', 'success')
    else:
        flash('Invalid transaction or already returned.', 'error')
    conn.close()
    return redirect(url_for('circulation'))

if __name__ == '__main__':
    app.run(debug=True)
