# library-management
CONSTANT DATA_FILE = "library_data.json"


CLASS Book:
    FIELDS: isbn, title, author, quantity, available

    CONSTRUCTOR(isbn, title, author, quantity, available = NULL):
        set isbn, title, author, quantity
        IF available is NULL:
            available = quantity        // new book: all copies available
        ELSE:
            available = available

    METHOD to_dict():
        RETURN {isbn, title, author, quantity, available} as dictionary

    STATIC METHOD from_dict(data):
        RETURN new Book(data.isbn, data.title, data.author,
                         data.quantity, data.available)

    METHOD to_string():
        RETURN "[isbn] 'title' by author - available/quantity available"


CLASS Library:
    FIELDS: books (map: isbn -> Book), issued_log (list of records)

    CONSTRUCTOR():
        books = empty map
        issued_log = empty list
        CALL load_data()

    METHOD load_data():
        IF DATA_FILE exists on disk:
            READ and PARSE JSON from DATA_FILE
            FOR EACH (isbn, bookData) in parsed "books":
                books[isbn] = Book.from_dict(bookData)
            issued_log = parsed "issued_log" (or empty list if missing)

    METHOD save_data():
        BUILD data = {
            "books": map of isbn -> book.to_dict() for each book,
            "issued_log": issued_log
        }
        WRITE data as JSON to DATA_FILE

    // ---------- Core operations ----------

    METHOD add_book(isbn, title, author, quantity):
        IF isbn already exists in books:
            increase existing book's quantity by quantity
            increase existing book's available by quantity
            PRINT "Added more copies"
        ELSE:
            books[isbn] = new Book(isbn, title, author, quantity)
            PRINT "Book added successfully"
        CALL save_data()

    METHOD remove_book(isbn):
        IF isbn exists in books:
            REMOVE and store the book
            CALL save_data()
            PRINT "Removed book"
        ELSE:
            PRINT "Book not found"

    METHOD search_book(keyword):
        keyword = lowercase(keyword)
        results = all books where:
            keyword is substring of lowercase(title)
            OR keyword is substring of lowercase(author)
            OR keyword equals lowercase(isbn)
        IF results not empty:
            PRINT count and each matching book
        ELSE:
            PRINT "No matching books found"
        RETURN results

    METHOD list_books():
        IF books is empty:
            PRINT "No books in library yet"
            RETURN
        PRINT header
        FOR EACH book in books:
            PRINT book

    METHOD issue_book(isbn, member_name):
        book = books.get(isbn)
        IF book does not exist:
            PRINT "Book not found"
            RETURN
        IF book.available <= 0:
            PRINT "No available copies"
            RETURN
        DECREMENT book.available by 1
        APPEND to issued_log: {
            isbn, title, member_name,
            date_issued = today's date,
            returned = FALSE
        }
        CALL save_data()
        PRINT "Book issued to member"

    METHOD return_book(isbn, member_name):
        book = books.get(isbn)
        IF book does not exist:
            PRINT "Book not found"
            RETURN

        FOR EACH record in issued_log, iterated MOST RECENT FIRST:
            IF record.isbn == isbn
               AND record.member == member_name
               AND record.returned == FALSE:
                SET record.returned = TRUE
                SET record.date_returned = today's date
                INCREMENT book.available by 1
                CALL save_data()
                PRINT "Book returned"
                RETURN

        PRINT "No matching issued record found"

    METHOD show_issued_books():
        active = all records in issued_log where returned == FALSE
        IF active is empty:
            PRINT "No books currently issued"
            RETURN
        PRINT header
        FOR EACH record in active:
            PRINT title, member, date_issued


FUNCTION print_menu():
    PRINT menu options 1-8 (Add, Remove, Search, List,
                             Issue, Return, Show Issued, Exit)


FUNCTION main():
    library = new Library()   // loads existing data on startup

    LOOP forever:
        CALL print_menu()
        choice = READ user input, trimmed

        MATCH choice:
            CASE "1":  // Add Book
                READ isbn, title, author
                READ quantity as integer
                IF quantity is not a valid number:
                    PRINT error, CONTINUE loop
                CALL library.add_book(isbn, title, author, quantity)

            CASE "2":  // Remove Book
                READ isbn
                CALL library.remove_book(isbn)

            CASE "3":  // Search Book
                READ keyword
                CALL library.search_book(keyword)

            CASE "4":  // List Books
                CALL library.list_books()

            CASE "5":  // Issue Book
                READ isbn, member name
                CALL library.issue_book(isbn, member)

            CASE "6":  // Return Book
                READ isbn, member name
                CALL library.return_book(isbn, member)

            CASE "7":  // Show Issued Books
                CALL library.show_issued_books()

            CASE "8":  // Exit
                PRINT "Goodbye!"
                BREAK loop

            DEFAULT:
                PRINT "Invalid choice"


ENTRY POINT: CALL main()
