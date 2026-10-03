import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database.db')

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database schema and seeds initial data."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Users Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('admin', 'faculty', 'student'))
    )
    ''')

    # 2. Students Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        roll_number TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        department TEXT NOT NULL,
        semester TEXT NOT NULL,
        email TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Active' CHECK(status IN ('Active', 'Suspended')),
        FOREIGN KEY (roll_number) REFERENCES users(username) ON DELETE CASCADE
    )
    ''')

    # 3. Faculty Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS faculty (
        faculty_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        department TEXT NOT NULL,
        designation TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT NOT NULL,
        avatar TEXT,
        FOREIGN KEY (faculty_id) REFERENCES users(username) ON DELETE CASCADE
    )
    ''')

    # 4. Attendance Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        student_roll TEXT NOT NULL,
        status TEXT NOT NULL CHECK(status IN ('P', 'A')),
        subject_code TEXT NOT NULL,
        FOREIGN KEY (student_roll) REFERENCES students(roll_number) ON DELETE CASCADE
    )
    ''')

    # 5. Notices Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS notices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        category TEXT NOT NULL,
        date_posted TEXT NOT NULL
    )
    ''')

    conn.commit()

    # Seed initial accounts and records if empty
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        print("Seeding database with default records...")
        
        # Hashed passwords
        admin_pass = generate_password_hash("admin123")
        faculty_pass = generate_password_hash("faculty123")
        student_pass = generate_password_hash("student123")

        # 1. Seed Users
        users = [
            ('admin', admin_pass, 'admin'),
            ('FAC2026101', faculty_pass, 'faculty'),
            ('FAC2026105', faculty_pass, 'faculty'),
            ('FAC2026118', faculty_pass, 'faculty'),
            ('FAC2026130', faculty_pass, 'faculty'),
            ('STU2026001', student_pass, 'student'),
            ('STU2026008', student_pass, 'student'),
            ('STU2026012', student_pass, 'student'),
            ('STU2026045', student_pass, 'student'),
            ('STU2026090', student_pass, 'student'),
            ('STU2026112', student_pass, 'student')
        ]
        cursor.executemany("INSERT INTO users VALUES (?, ?, ?)", users)

        # 2. Seed Faculty
        faculty_members = [
            ('FAC2026101', 'Dr. Ramesh K.', 'Computer Science', 'Head of Department', 'ramesh.k@edu.org', '+91 98765-10293', 'https://images.unsplash.com/photo-1560250097-0b93528c311a?auto=format&fit=crop&q=80&w=150&h=150'),
            ('FAC2026105', 'Prof. Arvinder Kaur', 'Computer Science', 'Associate Professor', 'arvinder.k@edu.org', '+91 98765-45601', 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&q=80&w=150&h=150'),
            ('FAC2026118', 'Dr. Vineet Garg', 'Electrical Eng.', 'Senior Lecturer', 'vineet.g@edu.org', '+91 98765-88225', 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&q=80&w=150&h=150'),
            ('FAC2026130', 'Ms. Priya Sharma', 'Mechanical Eng.', 'Assistant Professor', 'priya.sharma@edu.org', '+91 98765-72899', 'https://images.unsplash.com/photo-1580489944761-15a19d654956?auto=format&fit=crop&q=80&w=150&h=150')
        ]
        cursor.executemany("INSERT INTO faculty VALUES (?, ?, ?, ?, ?, ?, ?)", faculty_members)

        # 3. Seed Students
        student_records = [
            ('STU2026001', 'Aryan Sharma', 'Computer Science', '3rd Year / Sem 5', 'aryan.sharma@edu.org', 'Active'),
            ('STU2026008', 'Ishaan Verma', 'Computer Science', '3rd Year / Sem 5', 'ishaan.verma@edu.org', 'Active'),
            ('STU2026012', 'Meera Nair', 'Electrical Eng.', '2nd Year / Sem 3', 'meera.nair@edu.org', 'Active'),
            ('STU2026045', 'Kabir Mehta', 'Computer Science', '4th Year / Sem 7', 'kabir.mehta@edu.org', 'Active'),
            ('STU2026090', 'Priya Patel', 'Mechanical Eng.', '3rd Year / Sem 5', 'priya.patel@edu.org', 'Suspended'),
            ('STU2026112', 'Rohan Das', 'Civil Eng.', '1st Year / Sem 1', 'rohan.das@edu.org', 'Active')
        ]
        cursor.executemany("INSERT INTO students VALUES (?, ?, ?, ?, ?, ?)", student_records)

        # 4. Seed Notices
        notices_records = [
            ('Semester Exams Schedule Out', 'End semester exams begin next month on September 15.', 'Exam Cell', '2026-08-09'),
            ('Annual Tech Fest registrations', 'Register for hackathons & exhibitions in TechNexus \'26.', 'Clubs', '2026-08-08'),
            ('Independence Day Holiday', 'The campus will remain closed on August 15, 2026.', 'Dean Office', '2026-08-07')
        ]
        cursor.executemany("INSERT INTO notices (title, content, category, date_posted) VALUES (?, ?, ?, ?)", notices_records)

        # 5. Seed Attendance Logs
        # Setup initial attendance logs to show nice statistics
        attendance_logs = [
            ('2026-08-10', 'STU2026001', 'P', 'CS-501'),
            ('2026-08-10', 'STU2026008', 'P', 'CS-501'),
            ('2026-08-10', 'STU2026045', 'P', 'CS-501'),
            ('2026-08-10', 'STU2026090', 'A', 'CS-501'),
            
            ('2026-08-09', 'STU2026001', 'P', 'CS-501'),
            ('2026-08-09', 'STU2026008', 'A', 'CS-501'),
            ('2026-08-09', 'STU2026045', 'P', 'CS-501'),
            ('2026-08-09', 'STU2026090', 'A', 'CS-501'),

            ('2026-08-10', 'STU2026012', 'P', 'EE-302'),
            ('2026-08-10', 'STU2026112', 'P', 'CE-101')
        ]
        cursor.executemany("INSERT INTO attendance (date, student_roll, status, subject_code) VALUES (?, ?, ?, ?)", attendance_logs)

        conn.commit()

    conn.close()

# Helper queries for app.py
def verify_user(username, password):
    """Verifies user login credentials and returns (role, name, avatar) if success."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash, role FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    
    if not row or not check_password_hash(row['password_hash'], password):
        conn.close()
        return None

    role = row['role']
    name = username
    avatar = None

    if role == 'student':
        cursor.execute("SELECT name FROM students WHERE roll_number = ?", (username,))
        student_row = cursor.fetchone()
        if student_row:
            name = student_row['name']
            avatar = 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&q=80&w=100&h=100'
    elif role == 'faculty':
        cursor.execute("SELECT name, avatar FROM faculty WHERE faculty_id = ?", (username,))
        faculty_row = cursor.fetchone()
        if faculty_row:
            name = faculty_row['name']
            avatar = faculty_row['avatar']
    else:
        name = "Administrator"
        avatar = 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?auto=format&fit=crop&q=80&w=100&h=100'

    conn.close()
    return {'username': username, 'role': role, 'name': name, 'avatar': avatar}

def get_stats():
    """Aggregates summary statistics for the dashboard."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM faculty")
    total_faculty = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM notices")
    total_notices = cursor.fetchone()[0]

    # Calculate overall attendance rate
    cursor.execute("SELECT COUNT(*) FROM attendance")
    total_logs = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM attendance WHERE status = 'P'")
    present_logs = cursor.fetchone()[0]

    attendance_rate = 100.0
    if total_logs > 0:
        attendance_rate = round((present_logs / total_logs) * 100, 1)

    conn.close()
    return {
        'total_students': total_students,
        'total_faculty': total_faculty,
        'total_notices': total_notices,
        'attendance_rate': f"{attendance_rate}%"
    }

def get_all_students(search_query=None, dept_filter=None, status_filter=None):
    """Retrieves all students, applying optional searches and filters."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM students WHERE 1=1"
    params = []

    if search_query:
        query += " AND (roll_number LIKE ? OR name LIKE ? OR email LIKE ?)"
        search_val = f"%{search_query}%"
        params.extend([search_val, search_val, search_val])

    if dept_filter and dept_filter != 'all':
        query += " AND department = ?"
        params.append(dept_filter)

    if status_filter and status_filter != 'all':
        query += " AND status = ?"
        params.append(status_filter)

    cursor.execute(query, params)
    students_rows = cursor.fetchall()
    
    # Enrich with student attendance percentages
    students = []
    for row in students_rows:
        student = dict(row)
        cursor.execute("SELECT COUNT(*) FROM attendance WHERE student_roll = ?", (row['roll_number'],))
        total = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM attendance WHERE student_roll = ? AND status = 'P'", (row['roll_number'],))
        present = cursor.fetchone()[0]
        
        student['attendance_pct'] = f"{round((present / total * 100), 1)}%" if total > 0 else "100.0%"
        students.append(student)

    conn.close()
    return students

def add_student(roll, name, dept, sem, email, status):
    """Adds a new student and generates their default credentials."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Create user account
        default_pass = generate_password_hash("student123")
        cursor.execute("INSERT OR REPLACE INTO users (username, password_hash, role) VALUES (?, ?, 'student')", (roll, default_pass))
        # Create student profile
        cursor.execute("INSERT OR REPLACE INTO students (roll_number, name, department, semester, email, status) VALUES (?, ?, ?, ?, ?, ?)", 
                       (roll, name, dept, sem, email, status))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print("SQL Error:", e)
        return False
    finally:
        conn.close()

def delete_student(roll):
    """Deletes a student record and their associated user account."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM users WHERE username = ?", (roll,))
        cursor.execute("DELETE FROM students WHERE roll_number = ?", (roll,))
        cursor.execute("DELETE FROM attendance WHERE student_roll = ?", (roll,))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print("SQL Error:", e)
        return False
    finally:
        conn.close()

def get_all_faculty(search_query=None, dept_filter=None):
    """Retrieves all faculty members, applying optional searches and filters."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM faculty WHERE 1=1"
    params = []

    if search_query:
        query += " AND (faculty_id LIKE ? OR name LIKE ? OR designation LIKE ?)"
        search_val = f"%{search_query}%"
        params.extend([search_val, search_val, search_val])

    if dept_filter and dept_filter != 'all':
        query += " AND department = ?"
        params.append(dept_filter)

    cursor.execute(query, params)
    faculty = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return faculty

def add_faculty(fac_id, name, dept, desig, email, phone):
    """Adds a new faculty member and generates their default credentials."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Create user account
        default_pass = generate_password_hash("faculty123")
        cursor.execute("INSERT OR REPLACE INTO users (username, password_hash, role) VALUES (?, ?, 'faculty')", (fac_id, default_pass))
        # Choose a mock avatar
        avatar = 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&q=80&w=150&h=150'
        cursor.execute("INSERT OR REPLACE INTO faculty VALUES (?, ?, ?, ?, ?, ?, ?)", 
                       (fac_id, name, dept, desig, email, phone, avatar))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print("SQL Error:", e)
        return False
    finally:
        conn.close()

def delete_faculty(fac_id):
    """Deletes a faculty member profile and user account."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM users WHERE username = ?", (fac_id,))
        cursor.execute("DELETE FROM faculty WHERE faculty_id = ?", (fac_id,))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print("SQL Error:", e)
        return False
    finally:
        conn.close()

def get_notices():
    """Retrieves all active system notices."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notices ORDER BY id DESC")
    notices = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return notices

def get_students_for_attendance(dept=None):
    """Returns student list specifically for attendance tracking."""
    conn = get_db_connection()
    cursor = conn.cursor()
    if dept and dept != 'all':
        cursor.execute("SELECT roll_number, name, department, semester FROM students WHERE department = ? AND status = 'Active'", (dept,))
    else:
        cursor.execute("SELECT roll_number, name, department, semester FROM students WHERE status = 'Active'")
    students = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return students

def save_attendance(date, subject, attendance_data):
    """Saves attendance checklist submission. attendance_data is a dict {roll: 'P'/'A'}"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Delete existing logs for this subject on this date to overwrite
        cursor.execute("DELETE FROM attendance WHERE date = ? AND subject_code = ?", (date, subject))
        
        # Batch insert new logs
        logs = []
        for roll, status in attendance_data.items():
            logs.append((date, roll, status, subject))
        
        cursor.executemany("INSERT INTO attendance (date, student_roll, status, subject_code) VALUES (?, ?, ?, ?)", logs)
        conn.commit()
        return True
    except sqlite3.Error as e:
        print("SQL Error:", e)
        return False
    finally:
        conn.close()
