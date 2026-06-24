import matplotlib.pyplot as plt
from datetime import date
import db


def register_user(userid, username, password):
    conn = db.get_connection()
    cursor = conn.cursor(buffered=True)
    try:
        cursor.execute(
            "SELECT userid FROM users WHERE userid=%s",
            (userid,)
        )

        if cursor.fetchone():
            print("User ID already exists.")
            return False

        cursor.execute(
            "INSERT INTO users (userid, username, password) VALUES (%s,%s,%s)",
            (userid, username, password)
        )

        conn.commit()
        return True

    finally:
        cursor.close()
        conn.close()


def authenticate_user(userid, password):
    conn = db.get_connection()
    cursor = conn.cursor(buffered=True)
    try:
        cursor.execute("SELECT password, username FROM users WHERE userid=%s", (userid,))
        row = cursor.fetchone()
        if not row:
            return None
        stored_hash, username = row
        if password == stored_hash:
            return (userid, username)
        return None
    finally:
        cursor.close()
        conn.close()


def add_book(b_id, title, author, genre, year, quan):
    conn = db.get_connection()
    cursor = conn.cursor()
    try:
        if b_id is None or b_id == "":
            cursor.execute("INSERT INTO books (title, author, genre, year, quantity) VALUES (%s,%s,%s,%s,%s)",
                           (title, author, genre, year, quan))
        else:
            cursor.execute("INSERT INTO books (b_id, title, author, genre, year, quantity) VALUES (%s,%s,%s,%s,%s,%s)",
                           (int(b_id), title, author, genre, year, quan))
        conn.commit()
        print("Book added successfully.")
    finally:
        cursor.close()
        conn.close()


def view_books():
    conn = db.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM books")
        res = cursor.fetchall()
        if res:
            for book in res:
                print(book)
        else:
            print("Oops...No Book is available")
    finally:
        cursor.close()
        conn.close()

def delete_book(book_id):
    conn = db.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM books WHERE b_id=%s", (int(book_id),))
        book = cursor.fetchone()

        if not book:
            print("Book not found.")
            return

        # Check if the book is currently issued
        cursor.execute(
            "SELECT * FROM issued_books WHERE b_id=%s",
            (int(book_id),)
        )

        if cursor.fetchone():
            print("Cannot delete. This book is currently borrowed by a user.")
            return

        cursor.execute(
            "DELETE FROM books WHERE b_id=%s",
            (int(book_id),)
        )

        conn.commit()
        print("Book deleted successfully.")

    finally:
        cursor.close()
        conn.close()


def update_ai_interest(genre):
    conn = db.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT count FROM user_interest WHERE genre=%s", (genre,))
        result = cursor.fetchone()
        if result:
            cursor.execute("UPDATE user_interest SET count=count+1 WHERE genre=%s", (genre,))
        else:
            cursor.execute("INSERT INTO user_interest (genre, count) VALUES (%s, 1)", (genre,))
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def search_books(keyword):
    conn = db.get_connection()
    cursor = conn.cursor()
    try:
        query = '''SELECT * FROM books WHERE title LIKE %s OR author LIKE %s OR genre LIKE %s'''
        param = ('%'+keyword+'%', '%'+keyword+'%', '%'+keyword+'%')
        cursor.execute(query, param)
        books = cursor.fetchall()
        if books:
            for book in books:
                print(book)
                update_ai_interest(book[3])
        else:
            print("No books found.")
    finally:
        cursor.close()
        conn.close()


def ai_recommend_books():
    conn = db.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT genre FROM user_interest ORDER BY count DESC LIMIT 1")
        result = cursor.fetchone()
        if not result:
            print("Not enough data for recommendations.")
            return
        ai_genre = result[0]
        print(f"\n🤖 AI Suggested Genre (In-Trend): {ai_genre}")
        choice = input("Type 'yes' to accept or enter another genre of your choice: ").strip().lower()
        if choice == "yes":
            final_genre = ai_genre
        else:
            final_genre = choice
        cursor.execute("SELECT title, author FROM books WHERE genre=%s LIMIT 5", (final_genre,))
        books = cursor.fetchall()
        if not books:
            print("No books found in this genre.")
            return
        print(f"\nRecommended books in genre: {final_genre}")
        for book in books:
            print(f"- {book[0]} by {book[1]}")
    finally:
        cursor.close()
        conn.close()


def genre_wise_count():
    conn = db.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT genre, COUNT(*) FROM books GROUP BY genre")
        results = cursor.fetchall()
        if not results:
            print("No books available.")
            return
        print("\n Number of books in each genre:")
        for genre, count in results:
            print(f"- {genre} : {count} books")
    finally:
        cursor.close()
        conn.close()


def genre_wise_count_graph():
    conn = db.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT genre, COUNT(*) FROM books GROUP BY genre")
        data = cursor.fetchall()
        if not data:
            print("No books available.")
            return
        genres = [row[0] for row in data]
        counts = [row[1] for row in data]
        plt.figure()
        plt.bar(genres, counts)
        plt.xlabel("Genre")
        plt.ylabel("Number of Books")
        plt.title("Genre-wise Book Count")
        plt.show()
    finally:
        cursor.close()
        conn.close()


def borrow_book(book_id, current_user_id):
    conn = db.get_connection()
    cursor = conn.cursor(buffered=True)
    try:
        cursor.execute("select * from books where b_id =%s and quantity>0", (int(book_id),))
        book = cursor.fetchone()
        cursor.execute("select * from issued_books where b_id=%s and userid=%s", (int(book_id), current_user_id))
        if cursor.fetchone():
            print("Already borrowed")
            return
        if not (book):
            print("Book is not available")
        else:
            cursor.execute("update books set quantity=quantity-1 where b_id=%s", (int(book_id),))
            cursor.execute("insert into issued_books(b_id,userid,issue_date,return_date) values(%s,%s,CURDATE(),DATE_ADD(CURDATE(),INTERVAL 14 DAY))", (int(book_id), current_user_id))
            conn.commit()
            cursor.execute("select return_date from issued_books where b_id=%s and userid=%s order by issue_id desc limit 1", (int(book_id), current_user_id))
            returndate = cursor.fetchone()[0]
            print(f"\nBook Borrowed successfully!\nNote: Return before {returndate}")
    finally:
        cursor.close()
        conn.close()


def return_book(book_id, current_user_id):
    conn = db.get_connection()
    cursor = conn.cursor(buffered=True)
    try:
        cursor.execute("select * from issued_books where userid=%s and b_id=%s", (current_user_id, int(book_id)))
        record = cursor.fetchone()
        if not (record):
            print("You didn't borrowed this book")
        else:
            cursor.execute("delete from issued_books where b_id=%s and userid=%s", (int(book_id), current_user_id))
            cursor.execute("update books set quantity=quantity+1 where b_id=%s", (int(book_id),))
            conn.commit()
            print("Book returned successfully")
    finally:
        cursor.close()
        conn.close()


def mybooks(current_user_id):
    conn = db.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT books.b_id, books.title, books.author, books.year FROM books JOIN issued_books ON books.b_id = issued_books.b_id WHERE issued_books.userid = %s", (current_user_id,))
        mybooks = cursor.fetchall()
        if not mybooks:
            print("No books borrowed")
        else:
            for b_id, title, author, year in mybooks:
                print(f"\nBook ID: {b_id}")
                print(f"Title: {title}")
                print(f"Author: {author}")
                print(f"Year: {year}")
    finally:
        cursor.close()
        conn.close()
