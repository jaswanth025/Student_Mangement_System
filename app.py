from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
from datetime import date
import re
import os
import sys
app = Flask(__name__)
app.secret_key = 'abcd21234455'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'python_sms'
mysql = MySQL(app)
@app.route('/')
@app.route('/login', methods =['GET', 'POST'])
def login():
    mesage = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM sms_user WHERE status="active" AND email = % s AND password = % s', (email, password, ))
        user = cursor.fetchone()
        if user:
            session['loggedin'] = True
            session['userid'] = user['id']
            session['name'] = user['first_name']
            session['email'] = user['email']
            session['role'] = user['type']
            mesage = 'Logged in successfully !'
            return redirect(url_for('dashboard'))
        else:
            mesage = 'Please enter correct email / password !'
    return render_template('login.html', mesage = mesage)
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('email', None)
    session.pop('name', None)
    session.pop('role', None)
    return redirect(url_for('login'))
@app.route("/dashboard", methods =['GET', 'POST'])
def dashboard():
    if 'loggedin' in session:
        return render_template("dashboard.html")
    return redirect(url_for('login'))
@app.route("/teacher", methods =['GET', 'POST'])
def teacher():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT t.teacher_id, t.teacher, s.subject FROM sms_teacher t LEFT JOIN sms_subjects s ON s.subject_id = t.subject_id')
        teachers = cursor.fetchall()
        cursor.execute('SELECT * FROM sms_subjects')
        subjects = cursor.fetchall()
        return render_template("teacher.html", teachers = teachers, subjects = subjects)
    return redirect(url_for('login'))
@app.route("/edit_teacher", methods =['GET'])
def edit_teacher():
    if 'loggedin' in session:
        teacher_id = request.args.get('teacher_id')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT t.teacher_id, t.teacher, s.subject FROM sms_teacher t LEFT JOIN sms_subjects s ON s.subject_id = t.subject_id WHERE t.teacher_id = %s', (teacher_id,))
        teachers = cursor.fetchall()
        cursor.execute('SELECT * FROM sms_subjects')
        subjects = cursor.fetchall()
        return render_template("edit_teacher.html", teachers = teachers, subjects = subjects)
    return redirect(url_for('login'))
@app.route("/save_teacher", methods =['GET', 'POST'])
def save_teacher():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if request.method == 'POST' and 'techer_name' in request.form and 'specialization' in request.form:
            techer_name = request.form['techer_name']
            specialization = request.form['specialization']
            action = request.form['action']
            if action == 'updateTeacher':
                teacherid = request.form['teacherid']
                cursor.execute('UPDATE sms_teacher SET teacher = %s, subject_id = %s WHERE teacher_id =% s', (techer_name, specialization, (teacherid, ), ))
                mysql.connection.commit()
            else:
                cursor.execute('INSERT INTO sms_teacher (`teacher`, `subject_id`) VALUES (%s, %s)', (techer_name, specialization))
                mysql.connection.commit()
            return redirect(url_for('teacher'))
        elif request.method == 'POST':
            msg = 'Please fill out the form field !'
        return redirect(url_for('teacher'))
    return redirect(url_for('login'))
@app.route("/delete_teacher", methods =['GET'])
def delete_teacher():
    if 'loggedin' in session:
        teacher_id = request.args.get('teacher_id')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('DELETE FROM sms_teacher WHERE teacher_id = % s', (teacher_id, ))
        mysql.connection.commit()
        return redirect(url_for('teacher'))
    return redirect(url_for('login'))
@app.route("/subject", methods =['GET', 'POST'])
def subject():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM sms_subjects')
        subjects = cursor.fetchall()
        return render_template("subject.html", subjects = subjects)
    return redirect(url_for('login'))
@app.route("/save_subject", methods =['GET', 'POST'])
def save_subject():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if request.method == 'POST' and 'subject' in request.form and 's_type' in request.form and 'code' in request.form:
            subject = request.form['subject']
            s_type = request.form['s_type']
            code = request.form['code']
            action = request.form['action']
            if action == 'updateSubject':
                subjectid = request.form['subjectid']
                cursor.execute('UPDATE sms_subjects SET subject = %s, type = %s, code = %s WHERE subject_id  =% s', (subject, s_type, code, (subjectid, ), ))
                mysql.connection.commit()
            else:
                cursor.execute('INSERT INTO sms_subjects (`subject`, `type`, `code`) VALUES (%s, %s, %s)', (subject, s_type, code, ))
                mysql.connection.commit()
            return redirect(url_for('subject'))
        elif request.method == 'POST':
            msg = 'Please fill out the form field !'
        return redirect(url_for('subject'))
    return redirect(url_for('login'))
@app.route("/edit_subject", methods =['GET'])
def edit_subject():
    if 'loggedin' in session:
        subject_id = request.args.get('subject_id')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT subject_id, subject, type, code FROM sms_subjects WHERE subject_id = %s', (subject_id,))
        subjects = cursor.fetchall()
        return render_template("edit_subject.html", subjects = subjects)
    return redirect(url_for('login'))
@app.route("/delete_subject", methods =['GET'])
def delete_subject():
    if 'loggedin' in session:
        subject_id = request.args.get('subject_id')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('DELETE FROM sms_subjects WHERE subject_id = % s', (subject_id, ))
        mysql.connection.commit()
        return redirect(url_for('subject'))
    return redirect(url_for('login'))
@app.route("/classes", methods =['GET', 'POST'])
def classes():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT c.id, c.name, s.section, t.teacher FROM sms_classes c LEFT JOIN sms_section s ON s.section_id = c.section LEFT JOIN sms_teacher t ON t.teacher_id = c.teacher_id')
        classes = cursor.fetchall()
        cursor.execute('SELECT * FROM sms_section')
        sections = cursor.fetchall()
        cursor.execute('SELECT * FROM sms_teacher')
        teachers = cursor.fetchall()
        return render_template("class.html", classes = classes, sections = sections, teachers = teachers)
    return redirect(url_for('login'))
@app.route("/edit_class", methods =['GET'])
def edit_class():
    if 'loggedin' in session:
        class_id = request.args.get('class_id')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT c.id, c.name, s.section, t.teacher FROM sms_classes c LEFT JOIN sms_section s ON s.section_id = c.section LEFT JOIN sms_teacher t ON t.teacher_id = c.teacher_id WHERE c.id = %s', (class_id,))
        classes = cursor.fetchall()
        cursor.execute('SELECT * FROM sms_section')
        sections = cursor.fetchall()
        cursor.execute('SELECT * FROM sms_teacher')
        teachers = cursor.fetchall()
        return render_template("edit_class.html", classes = classes, sections = sections, teachers = teachers)
    return redirect(url_for('login'))
@app.route("/save_class", methods =['GET', 'POST'])
def save_class():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if request.method == 'POST' and 'cname' in request.form:
            cname = request.form['cname']
            sectionid = request.form['sectionid']
            teacherid = request.form['teacherid']
            action = request.form['action']
            if action == 'updateClass':
                class_id = request.form['classid']
                cursor.execute('UPDATE sms_classes SET name = %s, section = %s, teacher_id = %s WHERE id  =%s', (cname, sectionid, teacherid, (class_id, ), ))
                mysql.connection.commit()
            else:
                cursor.execute('INSERT INTO sms_classes (`name`, `section`, `teacher_id`) VALUES (%s, %s, %s)', (cname, sectionid, teacherid))
                mysql.connection.commit()
            return redirect(url_for('classes'))
        elif request.method == 'POST':
            msg = 'Please fill out the form field !'
        return redirect(url_for('classes'))
    return redirect(url_for('login'))
@app.route("/delete_class", methods =['GET'])
def delete_class():
    if 'loggedin' in session:
        class_id = request.args.get('class_id')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('DELETE FROM sms_classes WHERE id = % s', (class_id, ))
        mysql.connection.commit()
        return redirect(url_for('classes'))
    return redirect(url_for('login'))
@app.route("/sections", methods =['GET', 'POST'])
def sections():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM sms_section')
        sections = cursor.fetchall()
        return render_template("sections.html", sections = sections)
    return redirect(url_for('login'))
@app.route("/edit_sections", methods =['GET'])
def edit_sections():
    if 'loggedin' in session:
        section_id = request.args.get('section_id')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM sms_section WHERE section_id = %s', (section_id,))
        sections = cursor.fetchall()
        return render_template("edit_section.html", sections = sections)
    return redirect(url_for('login'))
@app.route("/save_sections", methods =['GET', 'POST'])
def save_sections():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if request.method == 'POST' and 'section_name' in request.form:
            section_name = request.form['section_name']
            action = request.form['action']
            if action == 'updateSection':
                section_id = request.form['sectionid']
                cursor.execute('UPDATE sms_section SET section = %s WHERE section_id  =%s', (section_name, (section_id, ), ))
                mysql.connection.commit()
            else:
                cursor.execute('INSERT INTO sms_section (`section`) VALUES (%s)', (section_name, ))
                mysql.connection.commit()
            return redirect(url_for('sections'))
        elif request.method == 'POST':
            msg = 'Please fill out the form field !'
        return redirect(url_for('sections'))
    return redirect(url_for('login'))
@app.route("/delete_sections", methods =['GET'])
def delete_sections():
    if 'loggedin' in session:
        section_id = request.args.get('section_id')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('DELETE FROM sms_section WHERE section_id = % s', (section_id, ))
        mysql.connection.commit()
        return redirect(url_for('sections'))
    return redirect(url_for('login'))
@app.route("/student", methods =['GET', 'POST'])
def student():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT s.id, s.admission_no, s.roll_no, s.name, s.photo, c.name AS class, sec.section FROM sms_students s LEFT JOIN sms_section sec ON sec.section_id = s.section LEFT JOIN sms_classes c ON c.id = s.class')
        students = cursor.fetchall()
        cursor.execute('SELECT * FROM sms_classes')
        classes = cursor.fetchall()
        cursor.execute('SELECT * FROM sms_section')
        sections = cursor.fetchall()
        return render_template("student.html", students = students, classes = classes, sections = sections)
    return redirect(url_for('login'))
@app.route("/edit_student", methods =['GET'])
def edit_student():
    if 'loggedin' in session:
        student_id = request.args.get('student_id')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT s.id, s.admission_no, s.roll_no, s.name, s.photo, c.name AS class, sec.section FROM sms_students s LEFT JOIN sms_section sec ON sec.section_id = s.section LEFT JOIN sms_classes c ON c.id = s.class WHERE s.id = %s', (student_id,))
        students = cursor.fetchall()
        cursor.execute('SELECT * FROM sms_classes')
        classes = cursor.fetchall()
        cursor.execute('SELECT * FROM sms_section')
        sections = cursor.fetchall()
        return render_template("edit_student.html", students = students, classes = classes, sections = sections)
    return redirect(url_for('login'))
@app.route("/save_student", methods =['GET', 'POST'])
def save_student():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if request.method == 'POST' and 'section_name' in request.form:
            section_name = request.form['section_name']
            action = request.form['action']
            if action == 'updateStudent':
                section_id = request.form['sectionid']
                cursor.execute('UPDATE sms_section SET section = %s WHERE section_id  =%s', (section_name, (section_id, ), ))
                mysql.connection.commit()
            else:
                cursor.execute('INSERT INTO sms_section (`section`) VALUES (%s)', (section_name, ))
                mysql.connection.commit()
            return redirect(url_for('sections'))
        elif request.method == 'POST':
            msg = 'Please fill out the form field !'
        return redirect(url_for('sections'))
    return redirect(url_for('login'))
@app.route("/delete_student", methods =['GET'])
def delete_student():
    if 'loggedin' in session:
        student_id = request.args.get('student_id')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('DELETE FROM sms_students WHERE id = % s', (student_id, ))
        mysql.connection.commit()
        return redirect(url_for('student'))
    return redirect(url_for('login'))
if __name__ == "__main__":
    app.run()
    os.execv(__file__, sys.argv)
