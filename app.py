from flask import Flask, jsonify, request, render_template_string, redirect, url_for
from database import get_db_connection, init_db
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

init_db()

SECRET_API_KEY = "super-secret-key-123"

# ==========================================
# SHARED CSS / DESIGN SYSTEM
# ==========================================

SHARED_HEAD = """
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
:root {
    --bg: #F5F2ED;
    --surface: #FDFCF9;
    --surface-raised: #FFFFFF;
    --ink: #1A1816;
    --ink-2: #4A4744;
    --ink-3: #9A9490;
    --rule: #E2DDD6;
    --rule-dark: #C8C0B4;
    --accent: #2B5CE6;
    --accent-light: #EEF2FD;
    --pass-bg: #E8F5EE;
    --pass-text: #1A6B3C;
    --fail-bg: #FDECEA;
    --fail-text: #C0392B;
}
body { font-family: 'DM Sans', sans-serif; background: var(--bg); color: var(--ink); min-height: 100vh; font-size: 14px; }
</style>
"""

# ==========================================
# HTML VIEWS & FRONT-END
# ==========================================

@app.route('/')
def home():
    return redirect(url_for('list_students'))


@app.route('/students')
def list_students():
    conn = get_db_connection()
    if not conn:
        return "Database Connection Error", 500

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
        <title>Student Registry</title>
        """ + SHARED_HEAD + """
        <style>
        .shell { display: grid; grid-template-columns: 220px 1fr; min-height: 100vh; }

        /* Sidebar */
        aside { background: var(--ink); color: #E8E4DE; padding: 32px 0; position: sticky; top: 0; height: 100vh; display: flex; flex-direction: column; }
        .logo-block { padding: 0 24px 28px; border-bottom: 1px solid rgba(255,255,255,0.08); }
        .logo-sup { font-family: 'DM Mono', monospace; font-size: 9px; letter-spacing: 0.2em; text-transform: uppercase; color: rgba(255,255,255,0.3); margin-bottom: 4px; }
        .logo-title { font-family: 'DM Serif Display', serif; font-size: 22px; color: #FDFCF9; line-height: 1.1; }
        .logo-title em { font-style: italic; color: #A8B8F0; }
        nav { padding: 20px 12px; flex: 1; }
        .nav-label { font-size: 9px; font-weight: 500; letter-spacing: 0.18em; text-transform: uppercase; color: rgba(255,255,255,0.28); padding: 0 12px; margin-bottom: 6px; }
        .nav-item { display: flex; align-items: center; gap: 10px; padding: 9px 12px; border-radius: 8px; color: rgba(255,255,255,0.5); font-size: 13px; text-decoration: none; transition: all 0.15s; }
        .nav-item:hover { background: rgba(255,255,255,0.07); color: rgba(255,255,255,0.9); }
        .nav-item.active { background: rgba(255,255,255,0.1); color: #FDFCF9; font-weight: 500; }
        .nav-icon { width: 15px; height: 15px; flex-shrink: 0; opacity: 0.65; }
        .nav-item.active .nav-icon { opacity: 1; }
        .nav-sep { margin-top: 18px; }
        .sidebar-footer { padding: 14px 24px; border-top: 1px solid rgba(255,255,255,0.08); }
        .version-tag { font-family: 'DM Mono', monospace; font-size: 10px; color: rgba(255,255,255,0.2); }

        /* Main */
        main { padding: 40px 48px; overflow-y: auto; }
        .page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 32px; }
        .page-header h1 { font-family: 'DM Serif Display', serif; font-size: 34px; color: var(--ink); line-height: 1.1; }
        .page-header h1 em { font-style: italic; color: var(--accent); }
        .page-sub { font-size: 13px; color: var(--ink-3); margin-top: 4px; }

        .btn-primary { display: inline-flex; align-items: center; gap: 8px; background: var(--ink); color: #FDFCF9; padding: 10px 20px; border-radius: 10px; font-size: 13px; font-weight: 500; text-decoration: none; transition: all 0.15s; white-space: nowrap; }
        .btn-primary:hover { background: #2d2927; transform: translateY(-1px); box-shadow: 0 4px 12px rgba(0,0,0,0.18); }

        /* Stats */
        .stats-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 32px; }
        .stat-card { background: var(--surface-raised); border: 1px solid var(--rule); border-radius: 14px; padding: 20px; position: relative; overflow: hidden; }
        .stat-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; border-radius: 14px 14px 0 0; background: var(--rule); }
        .stat-card.c-blue::before { background: #2B5CE6; }
        .stat-card.c-purple::before { background: #7C3AED; }
        .stat-card.c-green::before { background: #16A34A; }
        .stat-card.c-red::before { background: #DC2626; }
        .stat-label { font-size: 10px; font-weight: 500; letter-spacing: 0.14em; text-transform: uppercase; color: var(--ink-3); margin-bottom: 10px; }
        .stat-value { font-family: 'DM Serif Display', serif; font-size: 36px; line-height: 1; color: var(--ink); }
        .stat-card.c-green .stat-value { color: #16A34A; }
        .stat-card.c-red .stat-value { color: #DC2626; }

        /* Table */
        .table-card { background: var(--surface-raised); border: 1px solid var(--rule); border-radius: 16px; overflow: hidden; }
        .table-header { display: flex; justify-content: space-between; align-items: center; padding: 20px 28px; border-bottom: 1px solid var(--rule); }
        .table-title { font-family: 'DM Serif Display', serif; font-size: 18px; }
        .record-count { font-family: 'DM Mono', monospace; font-size: 11px; color: var(--ink-3); background: var(--bg); padding: 4px 10px; border-radius: 20px; border: 1px solid var(--rule); }
        table { width: 100%; border-collapse: collapse; }
        thead th { padding: 12px 16px; text-align: left; font-size: 10px; font-weight: 500; letter-spacing: 0.14em; text-transform: uppercase; color: var(--ink-3); background: #FAFAF8; border-bottom: 1px solid var(--rule); }
        thead th:first-child { padding-left: 28px; }
        thead th:last-child { padding-right: 28px; text-align: right; }
        tbody tr { border-bottom: 1px solid var(--rule); transition: background 0.1s; }
        tbody tr:last-child { border-bottom: none; }
        tbody tr:hover { background: #FAFAF8; }
        td { padding: 14px 16px; color: var(--ink-2); vertical-align: middle; }
        td:first-child { padding-left: 28px; }
        td:last-child { padding-right: 28px; text-align: right; }
        .id-cell { font-family: 'DM Mono', monospace; font-size: 11px; color: var(--ink-3); }
        .name-cell { font-weight: 500; color: var(--ink); font-size: 14px; }
        .grade-cell { display: flex; align-items: center; gap: 10px; }
        .grade-num { font-family: 'DM Mono', monospace; font-size: 13px; font-weight: 500; color: var(--ink); min-width: 44px; }
        .grade-bar-wrap { width: 60px; height: 4px; background: var(--rule); border-radius: 2px; overflow: hidden; }
        .grade-bar { height: 100%; border-radius: 2px; }
        .badge { display: inline-flex; align-items: center; padding: 3px 9px; border-radius: 6px; font-size: 10px; font-weight: 500; letter-spacing: 0.08em; text-transform: uppercase; }
        .badge-pass { background: var(--pass-bg); color: var(--pass-text); }
        .badge-fail { background: var(--fail-bg); color: var(--fail-text); }
        .section-pill { background: var(--bg); color: var(--ink-2); padding: 4px 10px; border-radius: 6px; font-size: 12px; border: 1px solid var(--rule); }
        .action-btn { display: inline-flex; align-items: center; justify-content: center; width: 30px; height: 30px; border-radius: 8px; text-decoration: none; transition: all 0.15s; border: none; cursor: pointer; background: transparent; }
        .action-btn:hover { background: var(--bg); }
        .action-btn.edit { color: var(--accent); }
        .action-btn.del { color: var(--fail-text); }
        .action-btn.del:hover { background: var(--fail-bg); }
        .actions-wrap { display: inline-flex; gap: 2px; align-items: center; }
        .empty-state { padding: 60px 28px; text-align: center; }
        .empty-dash { font-family: 'DM Serif Display', serif; font-size: 48px; color: var(--rule-dark); margin-bottom: 10px; }
        .empty-text { color: var(--ink-3); font-size: 13px; }
        .page-footer { margin-top: 28px; padding-top: 18px; border-top: 1px solid var(--rule); display: flex; justify-content: space-between; align-items: center; }
        .footer-text { font-family: 'DM Mono', monospace; font-size: 10px; color: var(--ink-3); }
        .api-tag { background: var(--accent-light); color: var(--accent); padding: 3px 10px; border-radius: 6px; font-family: 'DM Mono', monospace; font-size: 10px; }
        </style>
    </head>
    <body>
    <div class="shell">
        <aside>
            <div class="logo-block">
                <div class="logo-sup">Academic Registry</div>
                <div class="logo-title">Student<br><em>Portal</em></div>
            </div>
            <nav>
                <div class="nav-label">Management</div>
                <a class="nav-item active" href="/students">
                    <svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.8"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
                    All Students
                </a>
                <a class="nav-item" href="/add_student_form">
                    <svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.8"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/></svg>
                    Add Student
                </a>
                <div class="nav-label nav-sep">API Endpoints</div>
                <a class="nav-item" href="/api/students">
                    <svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.8"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>
                    /api/students
                </a>
                <a class="nav-item" href="/api/summary">
                    <svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.8"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
                    /api/summary
                </a>
            </nav>
            <div class="sidebar-footer">
                <div class="version-tag">v1.0 · Flask + PostgreSQL</div>
            </div>
        </aside>

        <main>
            <div class="page-header">
                <div>
                    <h1>Student <em>Roster</em></h1>
                    <div class="page-sub">Manage records, track grades, and monitor class performance.</div>
                </div>
                <a href="/add_student_form" class="btn-primary">
                    <svg width="14" height="14" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
                    Add Student
                </a>
            </div>

            <div class="stats-row">
                <div class="stat-card c-blue">
                    <div class="stat-label">Total Students</div>
                    <div class="stat-value">{{students|length}}</div>
                </div>
                <div class="stat-card c-purple">
                    <div class="stat-label">Class Average</div>
                    <div class="stat-value">{{ "%.1f"|format(avg) }}</div>
                </div>
                <div class="stat-card c-green">
                    <div class="stat-label">Passed</div>
                    <div class="stat-value">{{passed}}</div>
                </div>
                <div class="stat-card c-red">
                    <div class="stat-label">Failed</div>
                    <div class="stat-value">{{failed}}</div>
                </div>
            </div>

            <div class="table-card">
                <div class="table-header">
                    <div class="table-title">All Records</div>
                    <div class="record-count">{{students|length}} entries</div>
                </div>
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Name</th>
                            <th>Grade</th>
                            <th>Status</th>
                            <th>Section</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for s in students %}
                        <tr>
                            <td><span class="id-cell">#{{ '%03d' % s.id }}</span></td>
                            <td><span class="name-cell">{{s.name}}</span></td>
                            <td>
                                <div class="grade-cell">
                                    <span class="grade-num">{{ "%.2f"|format(s.grade) }}</span>
                                    <div class="grade-bar-wrap">
                                        <div class="grade-bar" style="width:{{ s.grade }}%; background:{% if s.grade >= 75 %}#16A34A{% elif s.grade >= 50 %}#D97706{% else %}#DC2626{% endif %};"></div>
                                    </div>
                                </div>
                            </td>
                            <td>
                                {% if s.grade >= 75 %}
                                    <span class="badge badge-pass">Pass</span>
                                {% else %}
                                    <span class="badge badge-fail">Fail</span>
                                {% endif %}
                            </td>
                            <td><span class="section-pill">{{s.section}}</span></td>
                            <td>
                                <div class="actions-wrap">
                                    <a href="/edit_student/{{s.id}}" class="action-btn edit" title="Edit">
                                        <svg width="15" height="15" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5"/><path d="M17.5 2.5a2.121 2.121 0 013 3L12 14l-4 1 1-4 7.5-7.5z"/></svg>
                                    </a>
                                    <form action="/delete_student/{{s.id}}" method="POST" style="display:inline;margin:0">
                                        <button type="submit" class="action-btn del" title="Delete" onclick="return confirm('Delete {{s.name}}?')">
                                            <svg width="15" height="15" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/><path d="M10 11v6M14 11v6"/><path d="M9 6V4h6v2"/></svg>
                                        </button>
                                    </form>
                                </div>
                            </td>
                        </tr>
                        {% else %}
                        <tr>
                            <td colspan="6">
                                <div class="empty-state">
                                    <div class="empty-dash">—</div>
                                    <div class="empty-text">No students yet. Add one to get started.</div>
                                </div>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>

            <div class="page-footer">
                <div class="footer-text">Student Management System · Flask + PostgreSQL</div>
                <span class="api-tag">REST API active</span>
            </div>
        </main>
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
        <title>Add Student</title>
        """ + SHARED_HEAD + """
        <style>
        body { display: grid; place-items: center; padding: 24px; }
        .card { background: var(--surface-raised); border: 1px solid var(--rule); border-radius: 20px; width: 100%; max-width: 440px; overflow: hidden; }
        .card-top { background: var(--ink); padding: 28px 32px; }
        .back-link { display: inline-flex; align-items: center; gap: 6px; color: rgba(255,255,255,0.4); font-size: 12px; text-decoration: none; margin-bottom: 16px; transition: color 0.15s; }
        .back-link:hover { color: rgba(255,255,255,0.75); }
        .card-top h1 { font-family: 'DM Serif Display', serif; font-size: 26px; color: #FDFCF9; line-height: 1.15; }
        .card-top h1 em { font-style: italic; color: #A8B8F0; }
        .card-top p { color: rgba(255,255,255,0.38); font-size: 12px; margin-top: 5px; }
        .card-body { padding: 28px 32px 32px; }
        .field { margin-bottom: 20px; }
        label { display: block; font-size: 11px; font-weight: 500; letter-spacing: 0.1em; text-transform: uppercase; color: var(--ink-3); margin-bottom: 8px; }
        input[type="text"], input[type="number"] { width: 100%; padding: 11px 14px; border: 1.5px solid var(--rule); border-radius: 10px; font-family: 'DM Sans', sans-serif; font-size: 14px; color: var(--ink); background: #FAFAF8; outline: none; transition: all 0.15s; appearance: none; }
        input:focus { border-color: var(--accent); background: var(--surface-raised); box-shadow: 0 0 0 3px rgba(43,92,230,0.1); }
        input::placeholder { color: #C8C0B4; }
        .grade-hint { display: flex; justify-content: space-between; margin-top: 6px; }
        .grade-hint span { font-family: 'DM Mono', monospace; font-size: 10px; color: var(--ink-3); }
        .divider { height: 1px; background: var(--rule); margin: 8px 0 24px; }
        .btn-submit { width: 100%; padding: 13px; background: var(--ink); color: #FDFCF9; border: none; border-radius: 10px; font-family: 'DM Sans', sans-serif; font-size: 14px; font-weight: 500; cursor: pointer; transition: all 0.15s; }
        .btn-submit:hover { background: #2d2927; transform: translateY(-1px); box-shadow: 0 4px 14px rgba(0,0,0,0.18); }
        </style>
    </head>
    <body>
        <div class="card">
            <div class="card-top">
                <a href="/students" class="back-link">
                    <svg width="12" height="12" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5"><polyline points="15 18 9 12 15 6"/></svg>
                    Back to roster
                </a>
                <h1>Add <em>New</em><br>Student</h1>
                <p>Fill in the fields below to register a student.</p>
            </div>
            <div class="card-body">
                <form action="/add_student" method="POST">
                    <div class="field">
                        <label for="name">Full Name</label>
                        <input type="text" id="name" name="name" required autofocus placeholder="e.g. Juan Dela Cruz">
                    </div>
                    <div class="field">
                        <label for="grade">Grade</label>
                        <input type="number" id="grade" name="grade" step="0.01" min="0" max="100" required placeholder="0.00 – 100.00">
                        <div class="grade-hint">
                            <span>Min: 0</span>
                            <span>Pass threshold: 75</span>
                            <span>Max: 100</span>
                        </div>
                    </div>
                    <div class="field">
                        <label for="section">Section</label>
                        <input type="text" id="section" name="section" required placeholder="e.g. Zechariah">
                    </div>
                    <div class="divider"></div>
                    <button type="submit" class="btn-submit">Save Student Record</button>
                </form>
            </div>
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
        <title>Edit Student</title>
        """ + SHARED_HEAD + """
        <style>
        body { display: grid; place-items: center; padding: 24px; }
        .card { background: var(--surface-raised); border: 1px solid var(--rule); border-radius: 20px; width: 100%; max-width: 440px; overflow: hidden; }
        .card-top { background: #2A3550; padding: 28px 32px; }
        .back-link { display: inline-flex; align-items: center; gap: 6px; color: rgba(255,255,255,0.38); font-size: 12px; text-decoration: none; margin-bottom: 16px; transition: color 0.15s; }
        .back-link:hover { color: rgba(255,255,255,0.7); }
        .card-top h1 { font-family: 'DM Serif Display', serif; font-size: 26px; color: #FDFCF9; line-height: 1.15; }
        .card-top h1 em { font-style: italic; color: #F9C74F; }
        .id-badge { display: inline-flex; align-items: center; gap: 6px; background: rgba(255,255,255,0.08); color: rgba(255,255,255,0.45); font-family: 'DM Mono', monospace; font-size: 11px; padding: 4px 10px; border-radius: 6px; margin-top: 8px; }
        .card-body { padding: 28px 32px 32px; }
        .field { margin-bottom: 20px; }
        label { display: block; font-size: 11px; font-weight: 500; letter-spacing: 0.1em; text-transform: uppercase; color: var(--ink-3); margin-bottom: 8px; }
        input[type="text"], input[type="number"] { width: 100%; padding: 11px 14px; border: 1.5px solid var(--rule); border-radius: 10px; font-family: 'DM Sans', sans-serif; font-size: 14px; color: var(--ink); background: #FAFAF8; outline: none; transition: all 0.15s; appearance: none; }
        input:focus { border-color: var(--accent); background: var(--surface-raised); box-shadow: 0 0 0 3px rgba(43,92,230,0.1); }
        .grade-hint { display: flex; justify-content: space-between; margin-top: 6px; }
        .grade-hint span { font-family: 'DM Mono', monospace; font-size: 10px; color: var(--ink-3); }
        .divider { height: 1px; background: var(--rule); margin: 8px 0 24px; }
        .btn-submit { width: 100%; padding: 13px; background: #2A3550; color: #FDFCF9; border: none; border-radius: 10px; font-family: 'DM Sans', sans-serif; font-size: 14px; font-weight: 500; cursor: pointer; transition: all 0.15s; }
        .btn-submit:hover { background: #1e2840; transform: translateY(-1px); box-shadow: 0 4px 14px rgba(42,53,80,0.28); }
        </style>
    </head>
    <body>
        <div class="card">
            <div class="card-top">
                <a href="/students" class="back-link">
                    <svg width="12" height="12" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5"><polyline points="15 18 9 12 15 6"/></svg>
                    Back to roster
                </a>
                <h1>Edit <em>Student</em><br>Record</h1>
                <div class="id-badge">
                    <svg width="10" height="10" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><rect x="2" y="5" width="20" height="14" rx="2"/><line x1="2" y1="10" x2="22" y2="10"/></svg>
                    ID #{{ '%03d' % student.id }}
                </div>
            </div>
            <div class="card-body">
                <form method="POST">
                    <div class="field">
                        <label for="name">Full Name</label>
                        <input type="text" id="name" name="name" value="{{student['name']}}" required>
                    </div>
                    <div class="field">
                        <label for="grade">Grade</label>
                        <input type="number" id="grade" name="grade" value="{{student['grade']}}" step="0.01" min="0" max="100" required>
                        <div class="grade-hint">
                            <span>Min: 0</span>
                            <span>Pass threshold: 75</span>
                            <span>Max: 100</span>
                        </div>
                    </div>
                    <div class="field">
                        <label for="section">Section</label>
                        <input type="text" id="section" name="section" value="{{student['section']}}" required>
                    </div>
                    <div class="divider"></div>
                    <button type="submit" class="btn-submit">Update Student Record</button>
                </form>
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html, student=student)


# ==========================================
# CORE API ENDPOINTS (CRUD & Analytics)
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
