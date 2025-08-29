    def borrow_book(self, user_id, book_id, days=14):
        """Borrow a book with proper validation and transaction handling.
        
        Args:
            user_id: ID of the user borrowing the book
            book_id: ID of the book to borrow
            days: Number of days the book can be borrowed for (default: 14)
            
        Returns:
            tuple: (success: bool, message: str)
        """
        # Input validation
        if not all(isinstance(x, int) and x > 0 for x in (user_id, book_id, days)):
            return False, "Invalid input parameters"

        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('BEGIN TRANSACTION')

                try:
                    # 1. Verify book exists and is available
                    cursor.execute('''
                        SELECT id, title, available_quantity 
                        FROM books 
                        WHERE id = ?
                        FOR UPDATE
                    ''', (book_id,))
                    
                    book = cursor.fetchone()
                    if not book:
                        raise ValueError(f"Book with ID {book_id} not found")
                        
                    if book['available_quantity'] <= 0:
                        raise ValueError(f"Book '{book['title']}' is out of stock")

                    # 2. Verify user exists and is active
                    cursor.execute('''
                        SELECT id, full_name, status
                        FROM users 
                        WHERE id = ?
                    ''', (user_id,))
                    
                    user = cursor.fetchone()
                    if not user:
                        raise ValueError(f"User with ID {user_id} not found")
                        
                    if user['status'].lower() != 'active':
                        raise ValueError(f"User account is not active (Status: {user['status']})")

                    # 3. Check borrowing limit (default max 5 books)
                    cursor.execute('''
                        SELECT COUNT(*) as active_loans 
                        FROM transactions 
                        WHERE user_id = ? AND return_date IS NULL
                    ''', (user_id,))
                    
                    if cursor.fetchone()['active_loans'] >= 5:
                        raise ValueError("Maximum borrowing limit of 5 books reached")

                    # 4. Calculate due date and current timestamp
                    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    due_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')

                    # 5. Update book quantity
                    cursor.execute('''
                        UPDATE books 
                        SET available_quantity = available_quantity - 1,
                            updated_at = ?
                        WHERE id = ? AND available_quantity > 0
                    ''', (now, book_id))

                    if cursor.rowcount == 0:
                        raise ValueError("Failed to update book availability")

                    # 6. Create transaction record
                    cursor.execute('''
                        INSERT INTO transactions 
                        (user_id, book_id, borrow_date, due_date, status, created_at, updated_at)
                        VALUES (?, ?, ?, ?, 'borrowed', ?, ?)
                    ''', (user_id, book_id, now, due_date, now, now))

                    conn.commit()
                    return True, f"Successfully borrowed '{book['title']}'. Due: {due_date}"

                except ValueError as ve:
                    conn.rollback()
                    return False, str(ve)
                except Exception as e:
                    conn.rollback()
                    logger.error(f"Borrow error: {str(e)}")
                    return False, "Failed to process borrowing"

        except sqlite3.Error as e:
            logger.error(f"Database error in borrow_book: {str(e)}")
            return False, f"Database error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error in borrow_book: {str(e)}")
            return False, "An unexpected error occurred"
