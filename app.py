from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import database
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Initialize database tables and seed defaults on startup
database.init_db()

# Middleware to check if user is logged in
def is_logged_in():
    return 'user' in session

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if is_logged_in():
        return redirect(url_for('dashboard'))

    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')

        user_info = database.verify_user(username, password)
        
        if user_info and user_info['role'] == role:
            session['user'] = user_info
            return redirect(url_for('dashboard'))
        else:
            error = "Invalid credentials or role mismatch. Please try again."

    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if not is_logged_in():
        return redirect(url_for('login'))

    stats = database.get_stats()
    notices = database.get_notices()
    return render_template('dashboard.html', stats=stats, notices=notices, user=session['user'])

@app.route('/students', methods=['GET', 'POST'])
def students():
    if not is_logged_in():
        return redirect(url_for('login'))

    # Handle Add / Update Student via POST
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'delete':
            roll = request.form.get('roll_number')
            success = database.delete_student(roll)
            return jsonify({'success': success})
            
        else:
            roll = request.form.get('roll_number')
            name = request.form.get('name')
            dept = request.form.get('department')
            sem = request.form.get('semester')
            email = request.form.get('email')
            status = request.form.get('status', 'Active')
            
            success = database.add_student(roll, name, dept, sem, email, status)
            if success:
                flash("Student profile saved successfully!", "success")
            else:
                flash("Failed to save student profile. Roll number might already exist.", "danger")
            return redirect(url_for('students'))

    # GET requests: fetch with filters
    search = request.args.get('search')
    dept = request.args.get('department', 'all')
    status = request.args.get('status', 'all')

    student_list = database.get_all_students(search_query=search, dept_filter=dept, status_filter=status)
    return render_template('students.html', students=student_list, user=session['user'], search=search, selected_dept=dept, selected_status=status)

@app.route('/faculty', methods=['GET', 'POST'])
def faculty():
    if not is_logged_in():
        return redirect(url_for('login'))

    # Handle Add / Delete Faculty via POST
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'delete':
            fac_id = request.form.get('faculty_id')
            success = database.delete_faculty(fac_id)
            return jsonify({'success': success})
            
        else:
            fac_id = request.form.get('faculty_id')
            name = request.form.get('name')
            dept = request.form.get('department')
            desig = request.form.get('designation')
            email = request.form.get('email')
            phone = request.form.get('phone')
            
            success = database.add_faculty(fac_id, name, dept, desig, email, phone)
            if success:
                flash("Faculty profile created successfully!", "success")
            else:
                flash("Failed to create faculty profile.", "danger")
            return redirect(url_for('faculty'))

    # GET requests: fetch with filters
    search = request.args.get('search')
    dept = request.args.get('department', 'all')

    faculty_list = database.get_all_faculty(search_query=search, dept_filter=dept)
    return render_template('faculty.html', faculty=faculty_list, user=session['user'], search=search, selected_dept=dept)

@app.route('/attendance', methods=['GET', 'POST'])
def attendance():
    if not is_logged_in():
        return redirect(url_for('login'))

    # Handle attendance submission via POST
    if request.method == 'POST':
        date = request.form.get('date')
        subject = request.form.get('subject_code')
        
        # Parse attendance toggles
        attendance_dict = {}
        for key, value in request.form.items():
            if key.startswith('attendance_'):
                roll = key.replace('attendance_', '')
                attendance_dict[roll] = value
                
        success = database.save_attendance(date, subject, attendance_dict)
        if success:
            flash("Attendance checklist submitted successfully!", "success")
            return jsonify({'success': True})
        return jsonify({'success': False}), 500

    # GET requests: load lists
    selected_dept = request.args.get('department', 'Computer Science')
    
    # Map department values from filter form
    dept_map = {
        'cs': 'Computer Science',
        'me': 'Mechanical Eng.',
        'ee': 'Electrical Eng.',
        'ce': 'Civil Eng.',
        'Computer Science': 'Computer Science',
        'Mechanical Eng.': 'Mechanical Eng.',
        'Electrical Eng.': 'Electrical Eng.',
        'Civil Eng.': 'Civil Eng.'
    }
    dept_name = dept_map.get(selected_dept, 'Computer Science')

    students_list = database.get_students_for_attendance(dept_name)
    stats = database.get_stats() # Get general stats to show totals
    
    return render_template('attendance.html', students=students_list, stats=stats, user=session['user'], selected_dept=dept_name)

if __name__ == '__main__':
    app.run(debug=True, port=5000, use_reloader=False)
