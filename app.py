from flask import Flask, jsonify, request, render_template_string, redirect, url_for
from database import get_db_connection, init_db
from psycopg2.extras import RealDictCursor # Added for PostgreSQL dictionary support

app = Flask(__name__)

# Initialize the PostgreSQL database when the app starts
init_db()

SECRET_API_KEY = "super-secret-key-123"

# ==========================================
# 2. HTML VIEWS & FRONT-END (Premium UI)
# ==========================================

@app.route('/')
def home():
    return redirect(url_for('list_students'))

@app.route('/students')
def list_students():
    conn = get_db_connection()
    if not conn:
        return "Database Connection Error", 500
        
    # In PostgreSQL (psycopg2), we use RealDictCursor instead of dictionary=True
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    cursor.close()
    conn.close()

    grades = [float(s['grade']) for s in students]
    passed = len([g for g in grades if g >= 75])
    failed = len(grades) - passed
    avg = sum(grades) / len(grades) if grades else 0

    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Student API Dashboard</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
        <style> body { font-family: 'Inter', sans-serif; } </style>
    </head>
    <body class="bg-slate-50 text-slate-800 min-h-screen p-4 md:p-8">
        <div class="max-w-6xl mx-auto">
            <!-- Header -->
            <header class="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
                <div>
                    <h1 class="text-3xl font-bold text-slate-900 tracking-tight flex items-center gap-3">
                        <span class="text-indigo-600">🎓</span> Student API Dashboard
                    </h1>
                    <p class="text-slate-500 mt-1 text-sm md:text-base">Manage student records, grades, and analytics seamlessly.</p>
                </div>
                <a href="/add_student_form" class="inline-flex items-center justify-center bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-2.5 rounded-lg font-medium transition-all shadow-md hover:shadow-lg focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                    <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path></svg>
                    Add New Student
                </a>
            </header>

            <!-- Analytics Grid -->
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                <div class="bg-white rounded-xl p-6 shadow-sm border border-slate-100 flex items-center justify-between hover:shadow-md transition-shadow">
                    <div>
                        <p class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Total Students</p>
                        <h3 class="text-3xl font-extrabold text-slate-800">{{students|length}}</h3>
                    </div>
                    <div class="w-12 h-12 bg-blue-50 rounded-full flex items-center justify-center text-blue-600 text-xl">👥</div>
                </div>
                <div class="bg-white rounded-xl p-6 shadow-sm border border-slate-100 flex items-center justify-between hover:shadow-md transition-shadow">
                    <div>
                        <p class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Class Average</p>
                        <h3 class="text-3xl font-extrabold text-slate-800">{{ "%.1f"|format(avg) }}</h3>
                    </div>
                    <div class="w-12 h-12 bg-purple-50 rounded-full flex items-center justify-center text-purple-600 text-xl">📈</div>
                </div>
                <div class="bg-white rounded-xl p-6 shadow-sm border border-slate-100 flex items-center justify-between hover:shadow-md transition-shadow">
                    <div>
                        <p class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Passed</p>
                        <h3 class="text-3xl font-extrabold text-emerald-600">{{passed}}</h3>
                    </div>
                    <div class="w-12 h-12 bg-emerald-50 rounded-full flex items-center justify-center text-emerald-600 text-xl">🎉</div>
                </div>
                <div class="bg-white rounded-xl p-6 shadow-sm border border-slate-100 flex items-center justify-between hover:shadow-md transition-shadow">
                    <div>
                        <p class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Failed</p>
                        <h3 class="text-3xl font-extrabold text-rose-600">{{failed}}</h3>
                    </div>
                    <div class="w-12 h-12 bg-rose-50 rounded-full flex items-center justify-center text-rose-600 text-xl">⚠️</div>
                </div>
            </div>

            <!-- Table Section -->
            <div class="bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden">
                <div class="p-6 border-b border-slate-100 bg-slate-50/50">
                    <h2 class="text-lg font-semibold text-slate-800">Student Roster</h2>
                </div>
                <div class="overflow-x-auto">
                    <table class="w-full text-left border-collapse">
                        <thead>
                            <tr class="bg-slate-50 border-b border-slate-100 text-slate-400 text-xs uppercase tracking-wider">
                                <th class="p-4 pl-6 font-semibold">ID</th>
                                <th class="p-4 font-semibold">Student Name</th>
                                <th class="p-4 font-semibold">Grade</th>
                                <th class="p-4 font-semibold">Section</th>
                                <th class="p-4 pr-6 font-semibold text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-slate-100 text-slate-700">
                            {% for s in students %}
                            <tr class="hover:bg-slate-50/80 transition-colors">
                                <td class="p-4 pl-6 text-slate-400 font-medium">#{{s.id}}</td>
                                <td class="p-4 font-semibold text-slate-900">{{s.name}}</td>
                                <td class="p-4">
                                    <div class="flex items-center gap-3">
                                        <span class="font-bold text-slate-800">{{ "%.2f"|format(s.grade) }}</span>
                                        {% if s.grade >= 75 %}
                                            <span class="px-2.5 py-1 text-xs font-bold rounded-md bg-emerald-100 text-emerald-700 border border-emerald-200 shadow-sm">PASS</span>
                                        {% else %}
                                            <span class="px-2.5 py-1 text-xs font-bold rounded-md bg-rose-100 text-rose-700 border border-rose-200 shadow-sm">FAIL</span>
                                        {% endif %}
                                    </div>
                                </td>
                                <td class="p-4 text-slate-600">{{s.section}}</td>
                                <td class="p-4 pr-6 text-right space-x-1">
                                    <a href="/edit_student/{{s.id}}" class="inline-flex items-center justify-center p-2 text-indigo-500 hover:text-indigo-700 hover:bg-indigo-50 rounded-lg transition-colors" title="Edit">
                                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path></svg>
                                    </a>
                                    <form action="/delete_student/{{s.id}}" method="POST" class="inline-block m-0">
                                        <button type="submit" onclick="return confirm('Are you sure you want to delete {{s.name}}?')" class="inline-flex items-center justify-center p-2 text-rose-500 hover:text-rose-700 hover:bg-rose-50 rounded-lg transition-colors" title="Delete">
                                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                                        </button>
                                    </form>
                                </td>
                            </tr>
                            {% else %}
                            <tr>
                                <td colspan="5" class="p-12 text-center text-slate-500">
                                    <div class="flex flex-col items-center justify-center">
                                        <div class="text-5xl mb-4">📭</div>
                                        <p class="text-xl font-semibold text-slate-700">No students found.</p>
                                        <p class="text-sm mt-2 text-slate-400">Click 'Add New Student' to populate the dashboard.</p>
                                    </div>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <div class="mt-8 text-center text-slate-400 text-sm font-medium">
                <p>Student Management API &bull; Powered by Flask & Render PostgreSQL</p>
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html, students=students, avg=avg, passed=passed, failed=failed)

@app.route('/add_student_form')
def add_student_form():
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Add Student</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
        <style> body { font-family: 'Inter', sans-serif; } </style>
    </head>
    <body class="bg-slate-50 text-slate-800 min-h-screen p-4 flex items-center justify-center">
        <div class="w-full max-w-md bg-white rounded-2xl shadow-xl border border-slate-100 p-8">
            <div class="flex items-center gap-3 mb-8">
                <a href="/students" class="text-slate-400 hover:text-indigo-600 transition-colors bg-slate-50 p-2 rounded-full">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path></svg>
                </a>
                <h2 class="text-2xl font-bold text-slate-900 tracking-tight">Add New Student</h2>
            </div>
            
            <form action="/add_student" method="POST" class="space-y-5">
                <div>
                    <label class="block text-sm font-semibold text-slate-700 mb-1.5">Full Name</label>
                    <input type="text" name="name" required autofocus class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-indigo-600 focus:border-indigo-600 outline-none transition-all placeholder-slate-400 bg-slate-50 focus:bg-white" placeholder="e.g. Juan Dela Cruz">
                </div>
                <div>
                    <label class="block text-sm font-semibold text-slate-700 mb-1.5">Grade (0-100)</label>
                    <input type="number" step="0.01" name="grade" min="0" max="100" required class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-indigo-600 focus:border-indigo-600 outline-none transition-all placeholder-slate-400 bg-slate-50 focus:bg-white" placeholder="e.g. 85.50">
                </div>
                <div>
                    <label class="block text-sm font-semibold text-slate-700 mb-1.5">Section</label>
                    <input type="text" name="section" required class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-indigo-600 focus:border-indigo-600 outline-none transition-all placeholder-slate-400 bg-slate-50 focus:bg-white" placeholder="e.g. Zechariah">
                </div>
                <div class="pt-4">
                    <button type="submit" class="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3.5 rounded-xl transition-all shadow-md hover:shadow-lg hover:-translate-y-0.5 focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                        Save Student Record
                    </button>
                </div>
            </form>
        </div>
    </body>
    </html>
    """
    return render_template_string(html)

@app.route('/edit_student/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM students WHERE id = %s", (id,))
    student = cursor.fetchone()

    if not student:
        cursor.close()
        conn.close()
        return "Student not found. <a href='/students'>Go back</a>", 404

    if request.method == 'POST':
        name = request.form.get("name")
        section = request.form.get("section")
        try:
            grade = float(request.form.get("grade"))
            if grade < 0 or grade > 100:
                cursor.close()
                conn.close()
                return "Error: Grade must be between 0 and 100. <br><a href='/edit_student/{}'>Go back</a>".format(id), 400
        except ValueError:
            cursor.close()
            conn.close()
            return "Error: Grade must be a valid number. <br><a href='/edit_student/{}'>Go back</a>".format(id), 400

        cursor.execute("UPDATE students SET name=%s, grade=%s, section=%s WHERE id=%s", (name, grade, section, id))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('list_students'))

    cursor.close()
    conn.close()

    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Edit Student</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
        <style> body { font-family: 'Inter', sans-serif; } </style>
    </head>
    <body class="bg-slate-50 text-slate-800 min-h-screen p-4 flex items-center justify-center">
        <div class="w-full max-w-md bg-white rounded-2xl shadow-xl border border-slate-100 p-8">
            <div class="flex items-center gap-3 mb-8">
                <a href="/students" class="text-slate-400 hover:text-indigo-600 transition-colors bg-slate-50 p-2 rounded-full">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path></svg>
                </a>
                <h2 class="text-2xl font-bold text-slate-900 tracking-tight">Edit Student</h2>
            </div>
            
            <form method="POST" class="space-y-5">
                <div>
                    <label class="block text-sm font-semibold text-slate-700 mb-1.5">Full Name</label>
                    <input type="text" name="name" value="{{student['name']}}" required class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-indigo-600 focus:border-indigo-600 outline-none transition-all bg-slate-50 focus:bg-white">
                </div>
                <div>
                    <label class="block text-sm font-semibold text-slate-700 mb-1.5">Grade (0-100)</label>
                    <input type="number" step="0.01" name="grade" value="{{student['grade']}}" min="0" max="100" required class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-indigo-600 focus:border-indigo-600 outline-none transition-all bg-slate-50 focus:bg-white">
                </div>
                <div>
                    <label class="block text-sm font-semibold text-slate-700 mb-1.5">Section</label>
                    <input type="text" name="section" value="{{student['section']}}" required class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-indigo-600 focus:border-indigo-600 outline-none transition-all bg-slate-50 focus:bg-white">
                </div>
                <div class="pt-4">
                    <button type="submit" class="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3.5 rounded-xl transition-all shadow-md hover:shadow-lg hover:-translate-y-0.5 focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                        Update Student Record
                    </button>
                </div>
            </form>
        </div>
    </body>
    </html>
    """
    return render_template_string(html, student=student)

# ==========================================
# 3. CORE API ENDPOINTS (CRUD & Analytics)
# ==========================================

@app.route('/add_student', methods=['POST'])
def add_student():
    name = request.form.get("name")
    section = request.form.get("section")
    grade_str = request.form.get("grade")

    if not name or not grade_str or not section:
        return "Error: Missing fields. <br><a href='/add_student_form'>Go back</a>", 400

    try:
        grade = float(grade_str)
    except ValueError:
        return "Error: Grade must be a number. <br><a href='/add_student_form'>Go back</a>", 400

    if grade < 0 or grade > 100:
        return "Error: Grade must be between 0 and 100. <br><a href='/add_student_form'>Go back</a>", 400

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO students (name, grade, section) VALUES (%s, %s, %s)", (name, grade, section))
        conn.commit()
        cursor.close()
        conn.close()
    
    return redirect(url_for('list_students'))

@app.route('/delete_student/<int:id>', methods=['POST'])
def delete_student(id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM students WHERE id = %s", (id,))
        conn.commit()
        cursor.close()
        conn.close()
    return redirect(url_for('list_students'))

@app.route('/api/students', methods=['GET'])
def api_get_students():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM students")
        students = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Convert Decimal to float for JSON output
        for s in students:
            s['grade'] = float(s['grade'])
        return jsonify(students)
    return jsonify({"error": "DB Connection Error"}), 500

@app.route('/api/student/<int:id>', methods=['GET'])
def api_get_student(id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM students WHERE id = %s", (id,))
        student = cursor.fetchone()
        cursor.close()
        conn.close()

        if student:
            student['grade'] = float(student['grade'])
            return jsonify(student)
    return jsonify({"error": "Student not found"}), 404

@app.route('/api/summary', methods=['GET'])
def api_summary():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT grade FROM students")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        if not rows:
             return jsonify({"average": 0, "passed": 0, "failed": 0})
        
        grades = [float(r['grade']) for r in rows]
        passed = len([g for g in grades if g >= 75])
        failed = len(grades) - passed
        avg = sum(grades) / len(grades)
        return jsonify({"average": avg, "passed": passed, "failed": failed})
    return jsonify({"error": "DB Connection Error"}), 500

if __name__ == '__main__':
    app.run(debug=True)
