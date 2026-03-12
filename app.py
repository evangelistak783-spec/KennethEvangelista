from flask import Flask, jsonify, render_template

app = Flask(__name__)

# Data - Moving this to a variable so both the API and the UI can use it
student_data = {
    "name": "Your Name",
    "grade": 10,
    "section": "Zechariah"
}

@app.route('/')
def home():
    # This renders the HTML file from the templates folder
    return render_template('index.html', student=student_data)

@app.route('/student')
def get_student():
    # This remains your raw API endpoint
    return jsonify(student_data)

if __name__ == '__main__':
    app.run(debug=True)
