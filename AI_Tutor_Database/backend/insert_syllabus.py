import pdfplumber
from litellm import completion
#from jinja2 import Environment, FileSystemLoader
import os
import json
import sqlite3
#import rag

from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

os.environ["GEMINI_API_KEY"] = os.getenv('GEMINI_API_KEY')

def pdf_txt_extract(filename):
    with pdfplumber.open(filename) as pdf:
        full_txt=""
        for page in pdf.pages:
            full_txt+=page.extract_text()
        return full_txt

def syllabus_txt_to_json(syllabus_txt):
    messages = [
        {
            "role": "user",
            "content": "Extract the course structure from the syllabus text:\n "+syllabus_txt
        }
    ]

    response_schema = {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "title": "Course Structure",
                "description": "Schema for a course structure with modules, topics, and time allotments",
                "type": "object",
                "properties": {
                    "course": {
                        "type": "object", 
                        "properties": {
                            "course_code": { "type": "string", "description": "Course code with no spaces" },
                            "course_title": { "type": "string", "description": "Title of the course" },                            
                            "modules": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "module_title": { "type": "string", "description": "Title of the module without 'Module X' in it" },
                                        "duration": { "type": "string", "description": "Duration of the module in hours" },
                                        "topics": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "number": { "type": "string", "description": "Unique topic identifier" },
                                                    "title": { "type": "string", "description": "Title of the topic" },
                                                    "time": { "type": "integer", "description": "Time allotted to the topic in hours" }
                                                },
                                                "required": ["number", "title", "time"]
                                            }
                                        }
                                    },
                                    "required": ["module_title", "duration", "topics"]
                                }
                            }
                        },
                        "required": ["course_code","course_title","modules"]
                    }
                },
                "required": ["course"]
            }


    res=completion(
        model="gemini/gemini-1.5-flash-8b", 
        messages=messages, 
        response_format={"type": "json_object", "response_schema": response_schema} 
        )
    return json.loads(res.choices[0].message.content)

def get_completion(message):
    messages = [
        {
            "role": "user",
            "content": message
        }
    ]
    res=completion(
        model="gemini/gemini-1.5-flash-8b", 
        messages=messages, 
    )
    return res.choices[0].message.content


#syllabus_json=json.load(open("out2.json",'r'))
#print(json.dumps(syllabus_json))




def read_pyq_papers():
    # Get the directory path for question papers
    pyq_dir = os.path.join('pyq')
    print(f"Looking for question papers in directory: {pyq_dir}")

    # Check if directory exists
    if not os.path.exists(pyq_dir):
        print(f"Directory {pyq_dir} does not exist")
        return {}

    # Get all PDF files in the directory
    pdf_files = [f for f in os.listdir(pyq_dir) if f.endswith('.pdf')]
    print(f"Found {len(pdf_files)} PDF files: {pdf_files}")

    if not pdf_files:
        print("No PDF files found in the directory")
        return {}

    # Combine text from all papers
    all_papers_text = ""
    for pdf_file in pdf_files:
        file_path = os.path.join(pyq_dir, pdf_file)
        print(f"\nProcessing file: {pdf_file}")
        try:
            paper_text = pdf_txt_extract(file_path)
            print(f"Successfully extracted text from {pdf_file} ({len(paper_text)} characters)")
            all_papers_text += paper_text + "\n\n"
        except Exception as e:
            print(f"Error processing {pdf_file}: {str(e)}")

    print(f"\nTotal combined text length: {len(all_papers_text)} characters")

    # Extract questions module-wise using AI
    num_modules = 5  # Adjust as needed
    module_questions = {}
    for module_number in range(1, num_modules + 1):
        print(f"\nProcessing Module {module_number}")
        prompt = f"Extract all questions of module {module_number} from these question papers. Remember that each module gets 2 questions in section 1 in order. Only return the questions, no other text."
        module_content = completion(
            model="gemini/gemini-2.0-flash-exp",
            messages=[
                {"role": "user", "content": prompt + "\n\nQuestion Papers:\n" + all_papers_text}
            ]
        ).choices[0].message.content
        print(f"Received response for Module {module_number} ({len(module_content)} characters)")

        # Store questions with module number as key
        module_questions[module_number] = module_content

    # Return the module_questions dictionary
    return module_questions

def insert_syllabus_into_db(syllabus_json):
    from rag import get_rag_completion
    conn = sqlite3.connect("syllabus.db")
    cursor = conn.cursor()
    course = syllabus_json["course"]
    course_code = course["course_code"]
    course_title = course["course_title"]

    # Check if the course already exists, if not insert it
    cursor.execute("SELECT id FROM courses WHERE course_code = ?", (course_code,))
    course_row = cursor.fetchone()
    if course_row is None:
        cursor.execute("""
            INSERT INTO courses (course_code, course_title) VALUES (?, ?)
        """, (course_code, course_title))
        course_id = cursor.lastrowid
    else:
        course_id = course_row[0]

    # Insert modules and their topics into the database
    module_ids = {}  # To keep track of module IDs for inserting topics
    for idx, module in enumerate(course["modules"], start=1):
        module_number = idx  # Assign module numbers using order index

        # Check if the module exists for this course
        cursor.execute("""
            SELECT id FROM modules WHERE course_id = ? AND module_number = ?
        """, (course_id, module_number))
        module_row = cursor.fetchone()
        if module_row is None:
            cursor.execute("""
                INSERT INTO modules (course_id, module_number, module_title, duration)
                VALUES (?, ?, ?, ?)
            """, (course_id, module_number, module["module_title"], module["duration"]))
            module_id = cursor.lastrowid
        else:
            module_id = module_row[0]

        module_ids[module_number] = module_id

        # Insert topics for the current module
        for topic in module["topics"]:
            # Check if the topic already exists for this module
            cursor.execute("""
                SELECT id FROM topics WHERE module_id = ? AND title = ?
            """, (module_id, topic["title"]))
            topic_row = cursor.fetchone()
            if topic_row is None:
                # Generate content for the topic if it doesn't exist
                topic_content = get_rag_completion(
                    f'In the context of a college course on "{course_title}", create course text for the topic "{topic["title"]}". '
                    f'Use available documents as context with attribution. Explain in some detail.'
                )
                cursor.execute("""
                    INSERT INTO topics (module_id, number, title, time, content)
                    VALUES (?, ?, ?, ?, ?)
                """, (module_id, topic["number"], topic["title"], topic["time"], topic_content))
            else:
                print(f"Topic '{topic['title']}' already exists in module '{module['module_title']}', skipping.")
                
    # Insert questions into the 'questions' table
    # Assuming questions are extracted and processed from external sources
    module_questions = {}  # Dictionary of {module_number: list_of_questions}
    try:
        module_questions = read_pyq_papers()  # Extract questions module-wise
    except Exception as e:
        print("Error while processing question papers:", str(e))

    for module_number, questions in module_questions.items():
        module_id = module_ids.get(module_number)
        if module_id is None:
            print(f"No module ID found for module number {module_number}. Skipping questions.")
            continue

        # Split questions into individual entries (if necessary)
        question_list = [q.strip() for q in questions.strip().split('\n\n') if q.strip()]
        for question in question_list:
            # Check if the question already exists for this module
            cursor.execute("""
                SELECT id FROM questions WHERE module_id = ? AND question_text = ?
            """, (module_id, question))
            question_row = cursor.fetchone()
            if question_row is None:
                # Insert the question
                cursor.execute("""
                    INSERT INTO questions (module_id, question_text)
                    VALUES (?, ?)
                """, (module_id, question))
            else:
                print(f"Question already exists in module {module_number}, skipping.")

    conn.commit()
    conn.close()
    print(f"Syllabus and related content for course '{course_title}' successfully stored in the database.")

if __name__ == "__main__":
    syllabus_txt=pdf_txt_extract('CST303.pdf')
    syllabus_json=syllabus_txt_to_json(syllabus_txt)
    print(syllabus_json)
    insert_syllabus_into_db(syllabus_json)
    #read_pyq_papers()
