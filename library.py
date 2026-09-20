

import json
import os
from datetime import datetime

DATA_FILE = "library_data.json"


class Book:
    def __init__(self, isbn, title, author, quantity, available=None):
        self.isbn = isbn
        self.title = title
        self.author = author
        self.quantity = quantity
        # available defaults to quantity if not provided (i.e. new book)
        self.available = available if available is not None else quantity

    def to_dict(self):
        return {
            "isbn": self.isbn,
            "title": self.title,
            "author": self.author,
            "quantity": self.quantity,
            "available": self.available,
        }

    @staticmethod
    def from_dict(data):
        return Book(
            data["isbn"], data["title"], data["author"],
            data["quantity"], data["available"]
        )

    def __str__(self):
        return (f"[{self.isbn}] '{self.title}' by {self.author} "
                f"- {self.available}/{self.quantity} available")


class Library:
    def __init__(self):
        self.books = {}       # isbn -> Book
        self.issued_log = []  # list of {isbn, member, date, returned}
        self.load_data()

    # ---------- Persistence ----------
    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                self.books = {
                    isbn: Book.from_dict(b) for isbn, b in data.get("books", {}).items()
                }
                self.issued_log = data.get("issued_log", [])

    def save_data(self):
        data = {
            "books": {isbn: book.to_dict() for isbn, book in self.books.items()},
            "issued_log": self.issued_log,
        }
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)

    # ---------- Core operations ----------
    def add_book(self, isbn, title, author, quantity):
        if isbn in self.books:
            # Book already exists, just add more copies
            self.books[isbn].quantity += quantity
            self.books[isbn].available += quantity
            print(f"Added {quantity} more copies of '{title}'.")
        else:
            self.books[isbn] = Book(isbn, title, author, quantity)
            print(f"Book '{title}' added successfully.")
        self.save_data()

    def remove_book(self, isbn):
        if isbn in self.books:
            removed = self.books.pop(isbn)
            self.save_data()
            print(f"Removed '{removed.title}'.")
        else:
            print("Book not found.")

    def search_book(self, keyword):
        keyword = keyword.lower()
        results = [
            book for book in self.books.values()
            if keyword in book.title.lower() or keyword in book.author.lower()
            or keyword == book.isbn.lower()
        ]
        if results:
            print(f"\nFound {len(results)} result(s):")
            for book in results:
                print(" ", book)
        else:
            print("No matching books found.")
        return results

    def list_books(self):
        if not self.books:
            print("No books in the library yet.")
            return
        print("\n--- Library Catalog ---")
        for book in self.books.values():
            print(" ", book)

    def issue_book(self, isbn, member_name):
        book = self.books.get(isbn)
        if not book:
            print("Book not found.")
            return
        if book.available <= 0:
            print(f"No available copies of '{book.title}' right now.")
            return
        book.available -= 1
        self.issued_log.append({
            "isbn": isbn,
            "title": book.title,
            "member": member_name,
            "date_issued": datetime.now().strftime("%Y-%m-%d"),
            "returned": False,
        })
        self.save_data()
        print(f"'{book.title}' issued to {member_name}.")

    def return_book(self, isbn, member_name):
        book = self.books.get(isbn)
        if not book:
            print("Book not found.")
            return

        # Find the most recent unreturned record for this member + book
        for record in reversed(self.issued_log):
            if (record["isbn"] == isbn and record["member"] == member_name
                    and not record["returned"]):
                record["returned"] = True
                record["date_returned"] = datetime.now().strftime("%Y-%m-%d")
                book.available += 1
                self.save_data()
                print(f"'{book.title}' returned by {member_name}.")
                return

        print("No matching issued record found (check name/ISBN).")

    def show_issued_books(self):
        active = [r for r in self.issued_log if not r["returned"]]
        if not active:
            print("No books are currently issued.")
            return
        print("\n--- Currently Issued Books ---")
        for r in active:
            print(f"  '{r['title']}' -> {r['member']} (issued {r['date_issued']})")


def print_menu():
    print("""
========= Library Management System =========
1. Add Book
2. Remove Book
3. Search Book
4. List All Books
5. Issue Book
6. Return Book
7. Show Issued Books
8. Exit
===============================================""")


def main():
    library = Library()

    while True:
        print_menu()
        choice = input("Enter your choice (1-8): ").strip()

        if choice == "1":
            isbn = input("ISBN: ").strip()
            title = input("Title: ").strip()
            author = input("Author: ").strip()
            try:
                quantity = int(input("Quantity: ").strip())
            except ValueError:
                print("Quantity must be a number.")
                continue
            library.add_book(isbn, title, author, quantity)

        elif choice == "2":
            isbn = input("Enter ISBN of book to remove: ").strip()
            library.remove_book(isbn)

        elif choice == "3":
            keyword = input("Search by title, author, or ISBN: ").strip()
            library.search_book(keyword)

        elif choice == "4":
            library.list_books()

        elif choice == "5":
            isbn = input("ISBN of book to issue: ").strip()
            member = input("Member name: ").strip()
            library.issue_book(isbn, member)

        elif choice == "6":
            isbn = input("ISBN of book to return: ").strip()
            member = input("Member name: ").strip()
            library.return_book(isbn, member)

        elif choice == "7":
            library.show_issued_books()

        elif choice == "8":
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Please enter a number from 1-8.")


if __name__ == "__main__":
    main()
