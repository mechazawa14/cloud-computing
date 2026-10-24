import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-student-management'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    roll_no = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    course = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return f'<Student {self.name}>'

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    students = Student.query.order_by(Student.id.desc()).all()
    return render_template('index.html', students=students)

@app.route('/add', methods=['POST'])
def add_student():
    roll_no = request.form.get('roll_no', '').strip()
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    course = request.form.get('course', '').strip()

    if not all([roll_no, name, email, course]):
        flash('Please fill in all fields.', 'error')
        return redirect(url_for('index'))

    existing = Student.query.filter_by(roll_no=roll_no).first()
    if existing:
        flash(f'Student with Roll No "{roll_no}" already exists.', 'error')
        return redirect(url_for('index'))

    new_student = Student(roll_no=roll_no, name=name, email=email, course=course)
    db.session.add(new_student)
    db.session.commit()
    flash('Student added successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    student = Student.query.get_or_404(id)

    if request.method == 'POST':
        roll_no = request.form.get('roll_no', '').strip()
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        course = request.form.get('course', '').strip()

        if not all([roll_no, name, email, course]):
            flash('Please fill in all fields.', 'error')
            return redirect(url_for('edit_student', id=id))

        # Check if another student has the same roll_no
        duplicate = Student.query.filter(Student.roll_no == roll_no, Student.id != id).first()
        if duplicate:
            flash(f'Roll No "{roll_no}" is already used by another student.', 'error')
            return redirect(url_for('edit_student', id=id))

        student.roll_no = roll_no
        student.name = name
        student.email = email
        student.course = course

        db.session.commit()
        flash('Student details updated successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('edit.html', student=student)

@app.route('/delete/<int:id>', methods=['POST'])
def delete_student(id):
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    flash(f'Student "{student.name}" deleted successfully.', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
