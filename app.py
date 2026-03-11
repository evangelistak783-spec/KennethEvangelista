from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/student')
def get_student():
    # Get grade from query parameter (default = 0)
    # Added a basic try-except to prevent crashing on non-numbers
    try:
        grade = int(request.args.get('grade', 0))
    except ValueError:
        return jsonify({"error": "Invalid grade provided. Please use a number."}), 400

    # Determine pass or fail
    remarks = "Pass" if grade >= 75 else "Fail"
    
    return jsonify({
        "name": "Juan",
        "grade": grade,
        "section": "Zechariah",
        "remarks": remarks
    })

if __name__ == '__main__':
    app.run(debug=True)
