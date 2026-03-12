from flask import Flask, jsonify, render_template

app = Flask(__name__)

# This is our "database" for now
student_data = {
    "name": "Your Name",
    "grade": 10,
    "section": "Zechariah"
}

@app.route('/')
def home():
    # render_template looks inside the /templates folder automatically
    return render_template('index.html', student=student_data)

@app.route('/student')
def get_student():
    return jsonify(student_data)

if __name__ == '__main__':
    app.run(debug=True)
