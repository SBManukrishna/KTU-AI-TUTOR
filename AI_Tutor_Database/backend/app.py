from flask import Flask, jsonify, send_from_directory, request
import os
import sqlite3
from werkzeug.utils import secure_filename
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Import functions from your pipeline file
from insert_syllabus import pdf_txt_extract, syllabus_txt_to_json, insert_syllabus_into_db

app = Flask(__name__, static_folder="../frontend")
CORS(app)

UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/<path:filename>")
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

# ----------------- FETCH AVAILABLE COURSES ----------------- #
@app.route("/api/courses", methods=["GET"])
def get_courses():
    conn = sqlite3.connect("syllabus.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, course_code, course_title FROM courses")
    courses = [{"id": row[0], "course_code": row[1], "course_title": row[2]} for row in cursor.fetchall()]
    conn.close()
    return jsonify(courses)



# ----------------- FETCH SYLLABUS FOR A SPECIFIC COURSE ----------------- #
# @app.route("/api/syllabus", methods=["GET"])
# def syllabus_api():
#     course_id = request.args.get("course_id")  # Get course_id from query params
#     return jsonify(get_syllabus(course_id))

@app.route("/api/syllabus", methods=["GET"])
def syllabus_api():
    course_id = request.args.get("course_id")
    if not course_id:
        return jsonify({"error": "Course ID is required"}), 400

    conn = sqlite3.connect("syllabus.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, module_number, module_title, duration FROM modules WHERE course_id = ?", (course_id,))
    modules = []
    for row in cursor.fetchall():
        module_id, module_number, module_title, duration = row
        module = {"module_number": module_number, "module_title": module_title, "duration": duration}
        
        cursor.execute("SELECT number, title, time, content FROM topics WHERE module_id = ?", (module_id,))
        topics = [{"number": t[0], "title": t[1], "time": t[2], "content": t[3]} for t in cursor.fetchall()]
        
        module["topics"] = topics
        modules.append(module)

    conn.close()
    return jsonify(modules)    
    
def get_syllabus(course_id=None):
    conn = sqlite3.connect("syllabus.db")
    cursor = conn.cursor()
    
    query = "SELECT id, course_code, course_title FROM courses"
    params = ()
    
    if course_id:
        query += " WHERE id = ?"
        params = (course_id,)
    
    cursor.execute(query, params)
    courses = []
    
    for row in cursor.fetchall():
        course_id, course_code, course_title = row
        course = {"id": course_id, "course_code": course_code, "course_title": course_title}
        
        cursor.execute("SELECT id, module_number, module_title, duration FROM modules WHERE course_id = ?", (course_id,))
        modules = []
        
        for mod_row in cursor.fetchall():
            module_id, module_number, module_title, duration = mod_row
            module = {"id": module_id, "module_number": module_number, "module_title": module_title, "duration": duration}
            
            cursor.execute("SELECT number, title, time, content FROM topics WHERE module_id = ?", (module_id,))
            topics = [{"number": t[0], "title": t[1], "time": t[2], "content": t[3]} for t in cursor.fetchall()]
            module["topics"] = topics
            modules.append(module)
        
        course["modules"] = modules
        courses.append(course)
    
    conn.close()
    return courses if course_id else courses  # Return all courses if no course_id provided

# ----------------- FETCH MODULE QUESTIONS ----------------- #
@app.route("/api/modules/<int:module_id>/questions", methods=["GET"])
def get_module_questions(module_id):
    conn = sqlite3.connect("syllabus.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT question_text FROM questions WHERE module_id = ?", (module_id,))
    questions = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    return jsonify(questions)

# ----------------- SYLLABUS UPLOAD ROUTE ----------------- #
@app.route("/api/upload-syllabus", methods=["POST"])
def upload_syllabus():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(file_path)
    
    try:
        # Process the PDF
        syllabus_txt = pdf_txt_extract(file_path)
        syllabus_json = syllabus_txt_to_json(syllabus_txt)
        insert_syllabus_into_db(syllabus_json)
        
        return jsonify({"success": "Syllabus uploaded and processed"}), 200
    except Exception as e:
        print("Error processing syllabus:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
