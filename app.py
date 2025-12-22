from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import pandas as pd
import numpy as np
import google.generativeai as genai
from auth import login_user, register_user, log_prediction
import os
from dotenv import load_dotenv
import json
import re

load_dotenv()

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    print("✓ Gemini API configured")
else:
    print("⚠ Warning: GEMINI_API_KEY not found")

# Load student data
try:
    df_students = pd.read_csv('student_data.csv')
    print(f"✓ Loaded {len(df_students)} student records")
except:
    print("⚠ student_data.csv not found. Run generate_data.py first!")
    df_students = None

def analyze_student_with_ai(student_data):
    """Use Gemini AI to analyze student and predict risk"""
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""You are an expert educational data scientist specializing in student performance prediction using Random Forest methodology.

**Student Profile:**
- ID: {student_data.get('student_id', 'N/A')}
- Age: {student_data.get('age', 'N/A')}
- Gender: {student_data.get('gender', 'N/A')}

**Academic Performance:**
- Attendance: {student_data.get('attendance_percentage', 0):.1f}%
- Assignment Score: {student_data.get('assignment_score', 0):.1f}/100
- Midterm Score: {student_data.get('midterm_score', 0):.1f}/100
- Participation Score: {student_data.get('participation_score', 0):.1f}/100
- Previous GPA: {student_data.get('previous_gpa', 0):.2f}/10.0

**Study Habits:**
- Study Hours/Week: {student_data.get('study_hours_per_week', 0):.1f} hours
- Sleep Hours: {student_data.get('sleep_hours', 0):.1f} hours/day

**External Factors:**
- Family Support: {student_data.get('family_support', 'N/A')}
- Internet Access: {student_data.get('internet_access', 'N/A')}
- Part-time Job: {student_data.get('part_time_job', 'N/A')}
- Commute Time: {student_data.get('commute_time_minutes', 0):.0f} minutes
- Financial Stress: {student_data.get('financial_stress', 'N/A')}
- Stress Level: {student_data.get('stress_level', 'N/A')}
- Scholarship: {student_data.get('scholarship', 'N/A')}
- Extracurricular: {student_data.get('extracurricular_activities', 'N/A')}

**Task:**
Using Random Forest classification logic, analyze this student and predict their risk category:
- **Green**: Likely to pass with high marks (75%+ expected)
- **Yellow**: Doing okay but needs support (55-75% expected)
- **Red**: High risk of failing (<55% expected)

**Return ONLY valid JSON (no markdown, no code blocks):**
{{
    "risk_category": "Green/Yellow/Red",
    "confidence": 85.5,
    "predicted_grade": 78.5,
    "key_risk_factors": [
        "Risk factor 1",
        "Risk factor 2",
        "Risk factor 3"
    ],
    "key_strengths": [
        "Strength 1",
        "Strength 2"
    ],
    "recommendations": [
        "Specific actionable recommendation 1",
        "Specific actionable recommendation 2",
        "Specific actionable recommendation 3"
    ],
    "intervention_priority": "High/Medium/Low",
    "analysis": "2-3 sentence explanation using Random Forest decision logic"
}}

**Important:** Base your prediction on multiple factors like a Random Forest would - attendance (40% weight), academic scores (30% weight), study habits (15% weight), and previous GPA (15% weight). Note: GPA is on a 0-10 scale.
"""
        
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Clean response
        response_text = response_text.replace('```json', '').replace('```', '').strip()
        
        # Extract JSON
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            result = json.loads(json_match.group())
        else:
            result = json.loads(response_text)
        
        return result
        
    except Exception as e:
        print(f"Error in AI analysis: {e}")
        return {
            "risk_category": "Yellow",
            "confidence": 50.0,
            "predicted_grade": 65.0,
            "key_risk_factors": ["Unable to analyze - API error"],
            "key_strengths": ["N/A"],
            "recommendations": ["Please try again"],
            "intervention_priority": "Medium",
            "analysis": f"Error: {str(e)}"
        }

def add_student_to_data(student_data):
    """Add a new student to the student_data.csv file"""
    global df_students
    
    try:
        # Create a new student record
        new_student = {
            'student_id': student_data.get('student_id', f"CUSTOM_{len(df_students) + 1}"),
            'name': student_data.get('name', 'Custom Student'),
            'age': student_data.get('age', 20),
            'gender': student_data.get('gender', 'Not Specified'),
            'attendance_percentage': student_data.get('attendance_percentage', 0),
            'assignment_score': student_data.get('assignment_score', 0),
            'midterm_score': student_data.get('midterm_score', 0),
            'participation_score': student_data.get('participation_score', 0),
            'study_hours_per_week': student_data.get('study_hours_per_week', 0),
            'previous_gpa': student_data.get('previous_gpa', 0),
            'family_support': student_data.get('family_support', 'Medium'),
            'internet_access': student_data.get('internet_access', 'Yes'),
            'part_time_job': student_data.get('part_time_job', 'No'),
            'commute_time_minutes': student_data.get('commute_time_minutes', 0),
            'scholarship': student_data.get('scholarship', 'No'),
            'financial_stress': student_data.get('financial_stress', 'Low'),
            'sleep_hours': student_data.get('sleep_hours', 7),
            'stress_level': student_data.get('stress_level', 'Low'),
            'extracurricular_activities': student_data.get('extracurricular_activities', 'No'),
            'final_grade': student_data.get('final_grade', 0),
            'risk_category': student_data.get('risk_category', 'Yellow')
        }
        
        # Add to dataframe
        df_students = pd.concat([df_students, pd.DataFrame([new_student])], ignore_index=True)
        
        # Save to CSV
        df_students.to_csv('student_data.csv', index=False)
        
        return True
    except Exception as e:
        print(f"Error adding student to data: {e}")
        return False

@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', user=session['user'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        success, result = login_user(username, password)
        
        if success:
            session['user'] = result
            return jsonify({'success': True, 'message': 'Login successful'})
        else:
            return jsonify({'success': False, 'message': result})
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.json
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        full_name = data.get('full_name')
        institution = data.get('institution')
        
        success, result = register_user(username, email, password, full_name, institution)
        
        return jsonify({'success': success, 'message': result})
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/api/students')
def get_students():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    if df_students is None:
        return jsonify({'error': 'No student data available'}), 404
    
    students = df_students[['student_id', 'name', 'risk_category']].to_dict('records')
    return jsonify(students)

@app.route('/api/predict', methods=['POST'])
def predict():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    student_id = data.get('student_id')
    
    if df_students is None:
        return jsonify({'error': 'No student data available'}), 404
    
    # Get student data
    student = df_students[df_students['student_id'] == student_id]
    
    if student.empty:
        return jsonify({'error': 'Student not found'}), 404
    
    student_data = student.iloc[0].to_dict()
    
    # Analyze with AI
    result = analyze_student_with_ai(student_data)
    
    # Log prediction
    log_prediction(
        session['user']['username'],
        student_id,
        result['risk_category'],
        result['confidence']
    )
    
    # Add student info to result
    result['student_id'] = student_data['student_id']
    result['student_name'] = student_data['name']
    result['attendance'] = student_data['attendance_percentage']
    result['assignment_score'] = student_data['assignment_score']
    result['midterm_score'] = student_data['midterm_score']
    result['previous_gpa'] = student_data['previous_gpa']
    
    return jsonify(result)

@app.route('/api/analyze-custom', methods=['POST'])
def analyze_custom():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    
    # Generate student ID if not provided
    if 'student_id' not in data or not data['student_id']:
        data['student_id'] = f"CUSTOM_{len(df_students) + 1}"
    
    # Analyze with AI
    result = analyze_student_with_ai(data)
    
    # Add the predicted grade and risk category to student data
    data['final_grade'] = result.get('predicted_grade', 0)
    data['risk_category'] = result['risk_category']
    
    # Add student to the database
    add_student_to_data(data)
    
    # Log prediction
    log_prediction(
        session['user']['username'],
        data['student_id'],
        result['risk_category'],
        result['confidence']
    )
    
    return jsonify(result)

@app.route('/api/stats')
def get_stats():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    if df_students is None:
        return jsonify({'error': 'No student data available'}), 404
    
    stats = {
        'total_students': len(df_students),
        'green': len(df_students[df_students['risk_category'] == 'Green']),
        'yellow': len(df_students[df_students['risk_category'] == 'Yellow']),
        'red': len(df_students[df_students['risk_category'] == 'Red']),
        'avg_attendance': float(df_students['attendance_percentage'].mean()),
        'avg_grade': float(df_students['final_grade'].mean())
    }
    
    return jsonify(stats)

if __name__ == '__main__':
    # Generate data if it doesn't exist
    if not os.path.exists('student_data.csv'):
        print("Generating student data...")
        from generate_data import generate_student_data
        generate_student_data(500)
    
    app.run(debug=True, port=5000)