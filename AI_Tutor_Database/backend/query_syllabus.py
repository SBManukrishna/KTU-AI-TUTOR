import sqlite3

def get_course_syllabus(course_code):
    conn = sqlite3.connect("syllabus.db")
    cursor = conn.cursor()

    # Fetch course details
    cursor.execute("SELECT course_title FROM courses WHERE course_code=?", (course_code,))
    course = cursor.fetchone()
    if not course:
        print("Course not found.")
        return

    print(f"Course: {course[0]}\n")

    # Fetch modules
    cursor.execute("SELECT id, module_title, duration FROM modules WHERE course_code=?", (course_code,))
    modules = cursor.fetchall()

    for module in modules:
        module_id, module_title, duration = module
        print(f"Module: {module_title} ({duration} hours)")

        # Fetch topics for each module
        cursor.execute("SELECT number, title, time, content FROM topics WHERE module_id=?", (module_id,))
        topics = cursor.fetchall()

        for topic in topics:
            number, title, time, content = topic
            print(f"  {number}. {title} ({time} hours)\n  {content}\n")

    conn.close()

# Example Usage:
if __name__ == "__main__":
    course_code = input("Enter Course Code: ")
    get_course_syllabus(course_code)
