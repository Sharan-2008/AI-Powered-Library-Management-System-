import os
import models

import dotenv
dotenv.load_dotenv()

def admin_menu():
    admin_pass = input("Enter Admin Password: ")
    if admin_pass != os.getenv('ADMIN_PASSWORD'):
        print("WARNING!...Invalid Admin login")
        return
    while True:
        print("""
-------------------------------------------------

        ADMIN BASE
    1. Add Book 
    2. Delete Book 
    3. View All Books
    4. Genre-wise Book count
    5. Bar-graph for books (genre wise)
    6. Exit

-------------------------------------------------
        """)
        choice = input("Select an option: ")
        if choice == '1':
            b_id = input("Book ID (leave blank for auto): ")
            models.add_book(
                b_id if b_id else None,
                input("Title: "),
                input("Author: "),
                input("Genre: "),
                int(input("Year: ")),
                int(input("Stock Quantity: "))
            )
        elif choice == '2':
            bid = input("Enter Book ID to delete: ")
            models.delete_book(bid)
        elif choice == '3':
            models.view_books()
        elif choice == '4':
            models.genre_wise_count()
        elif choice == '5':
            models.genre_wise_count_graph()
        elif choice == '6':
            print("Exiting.")
            break
        else:
            print("Invalid option. Please try again.")


def user_menu(user_tuple):
    current_user_id, _ = user_tuple
    while True:
        print("""
-----------------------------------------------

                  USER 
          1. View Books
          2. Search Books
          3. Borrow Book
          4. Return Book
          5. My Books
          6. Get Recommendation
          7. Exit
          
----------------------------------------------
        """)
        choice = input("Enter your choice:")
        if choice == "1":
            models.view_books()
        elif choice == "2":
            models.search_books(input("Enter keyword: "))
        elif choice == "3":
            models.borrow_book(input("Book ID: "), current_user_id)
        elif choice == "4":
            book_id = input("Enter Book ID: ")
            models.return_book(book_id, current_user_id)
        elif choice == "5":
            models.mybooks(current_user_id)
        elif choice == "6":
            models.ai_recommend_books()
        elif choice == "7":
            print("Exiting...")
            break
        else:
            print("Invalid choice")


def main():
    while True:
        print("""
Enter your Role:
    1. Admin
    2. User
    3. Register(New user)
    4. Exit
""")
        role = input("Select an option:")
        if role == "1":
            admin_menu()
        elif role == "2":
            user_ID = input("Enter User ID: ")
            user_pass = input("Enter Userpassword: ")
            user = models.authenticate_user(user_ID, user_pass)
            if user:
                print("Login successful")
                user_menu(user)
            else:
                print("Invalid Login...Try again!\nNote: Register if you are new user")
        elif role == "3":
            new_user_id = input("Create user Id: ")
            new_user_name = input("Create User name: ")
            new_user_password = input("Create new password: ")
            success = models.register_user(new_user_id, new_user_name, new_user_password)
            if success:
                print("New User Registered!")
            else:
                print("Registration failed. Try different user id.")
        elif role == "4":
            print("Thankyou! Visit us again")
            break
        else:
            print("invalid choice")


if __name__ == "__main__":
    main()
