#!/usr/bin/env python
import sqlite3

def setup_database():
    conn = sqlite3.connect("syllabus.db")
    cursor = conn.cursor()
    # Create 'courses' table with id and unique course_code
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_code TEXT UNIQUE,
            course_title TEXT
        )
    """)
    # Create 'modules' table referencing courses.id instead of course_code
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS modules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER,
            module_number INTEGER,
            module_title TEXT,
            duration TEXT,
            FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
        )
    """)
    # Create 'topics' table (no change needed here)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            module_id INTEGER,
            number TEXT,
            title TEXT,
            time INTEGER,
            content TEXT,
            FOREIGN KEY (module_id) REFERENCES modules(id) ON DELETE CASCADE
        )
    """)
    # Create 'questions' table (no change needed here)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            module_id INTEGER,
            question_text TEXT,
            FOREIGN KEY (module_id) REFERENCES modules(id) ON DELETE CASCADE
        )
    """)
    conn.commit()
    conn.close()
    print("Database and tables created/updated successfully.")

if __name__ == "__main__":
    setup_database()