import pandas as pd
import numpy as np
import random

def generate_student_data(num_students=500):
    """Generate synthetic student data"""
    
    np.random.seed(42)
    random.seed(42)
    
    data = []
    
    for i in range(num_students):
        # Basic info
        student_id = f"STU{1000 + i}"
        name = f"Student_{i+1}"
        age = random.randint(18, 25)
        gender = random.choice(['Male', 'Female'])
        
        # Academic factors
        attendance = round(random.uniform(30, 100), 2)
        assignment_score = round(random.uniform(20, 100), 2)
        midterm_score = round(random.uniform(25, 100), 2)
        participation = round(random.uniform(10, 100), 2)
        
        # Study habits
        study_hours_per_week = round(random.uniform(0, 40), 1)
        previous_gpa = round(random.uniform(3.0, 10.0), 2)
        
        # External factors
        family_support = random.choice(['Low', 'Medium', 'High'])
        internet_access = random.choice(['Yes', 'No'])
        part_time_job = random.choice(['Yes', 'No'])
        commute_time = round(random.uniform(10, 120), 0)  # minutes
        
        # Financial
        scholarship = random.choice(['Yes', 'No'])
        financial_stress = random.choice(['Low', 'Medium', 'High'])
        
        # Health & wellness
        sleep_hours = round(random.uniform(4, 9), 1)
        stress_level = random.choice(['Low', 'Medium', 'High'])
        extracurricular = random.choice(['Yes', 'No'])
        
        # Calculate risk score (for generating realistic labels)
        risk_score = 0
        
        # Attendance impact (40%)
        if attendance < 60:
            risk_score += 40
        elif attendance < 75:
            risk_score += 25
        elif attendance < 85:
            risk_score += 10
        
        # Academic performance impact (30%)
        avg_academic = (assignment_score + midterm_score) / 2
        if avg_academic < 50:
            risk_score += 30
        elif avg_academic < 65:
            risk_score += 20
        elif avg_academic < 75:
            risk_score += 10
        
        # Study habits impact (15%)
        if study_hours_per_week < 10:
            risk_score += 15
        elif study_hours_per_week < 20:
            risk_score += 8
        
        # Previous GPA impact (15%) - Updated for 0-10 scale
        if previous_gpa < 5.0:
            risk_score += 15
        elif previous_gpa < 6.5:
            risk_score += 10
        elif previous_gpa < 7.5:
            risk_score += 5
        
        # Additional factors
        if family_support == 'Low':
            risk_score += 5
        if internet_access == 'No':
            risk_score += 3
        if part_time_job == 'Yes':
            risk_score += 3
        if financial_stress == 'High':
            risk_score += 4
        if sleep_hours < 6:
            risk_score += 3
        if stress_level == 'High':
            risk_score += 3
        
        # Determine risk category
        if risk_score >= 70:
            risk_category = 'Red'  # High risk
            final_grade = round(random.uniform(30, 55), 2)
        elif risk_score >= 40:
            risk_category = 'Yellow'  # Medium risk
            final_grade = round(random.uniform(55, 75), 2)
        else:
            risk_category = 'Green'  # Low risk
            final_grade = round(random.uniform(75, 98), 2)
        
        data.append({
            'student_id': student_id,
            'name': name,
            'age': age,
            'gender': gender,
            'attendance_percentage': attendance,
            'assignment_score': assignment_score,
            'midterm_score': midterm_score,
            'participation_score': participation,
            'study_hours_per_week': study_hours_per_week,
            'previous_gpa': previous_gpa,
            'family_support': family_support,
            'internet_access': internet_access,
            'part_time_job': part_time_job,
            'commute_time_minutes': commute_time,
            'scholarship': scholarship,
            'financial_stress': financial_stress,
            'sleep_hours': sleep_hours,
            'stress_level': stress_level,
            'extracurricular_activities': extracurricular,
            'final_grade': final_grade,
            'risk_category': risk_category
        })
    
    df = pd.DataFrame(data)
    df.to_csv('student_data.csv', index=False)
    print(f"✓ Generated {num_students} student records")
    print(f"\nRisk Distribution:")
    print(df['risk_category'].value_counts())
    return df

if __name__ == "__main__":
    generate_student_data(500)