import os

from flask import Flask, render_template, request, redirect, url_for, flash
from Forms import CreateUserForm, patientLogin, UpdateUserForm, ForgotPasswordForm, EmployeeLogin, CreateBooking, OtpForm
import sqlite3 , random
from flask_mail import Mail, Message

# conn = sqlite3.connect('database.db')
# c = conn.cursor()

# c.execute("""CREATE TABLE bookings (
#      id           INTEGER PRIMARY KEY AUTOINCREMENT,
#      first_name   TEXT,
#      last_name    TEXT,
#      email        TEXT,
#      date         TEXT,
#      timeslot     TEXT,
#      remarks      TEXT,
#      availability TEXT,
#      doctor TEXT
# );""")
#
# c.execute("""CREATE TABLE patients (
#      id           INTEGER PRIMARY KEY AUTOINCREMENT,
#      first_name   TEXT,
#      last_name    TEXT,
#      gender       TEXT,
#      email        TEXT,
#      password     TEXT
#
#
# );""")



app = Flask(__name__)
app.secret_key = "shh"

app.config['MAIL_SERVER']='smtp.office365.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'prcaremanagement@outlook.com'
app.config['MAIL_PASSWORD'] = 'Dummyaccount'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)
@app.route('/')
def home():
    return render_template('home.html')


@app.route('/createUser', methods=['GET', 'POST'])
def create_user():
    create_user_form = CreateUserForm(request.form)
    if request.method == 'POST' and create_user_form.validate():
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        gender = request.form['gender']
        email = request.form['email'].lower()
        password = request.form['password']
        print(first_name, last_name, gender, email, password)
        c.execute(
            "INSERT INTO patients (first_name, last_name, gender, email, password) VALUES ('" + first_name + "','" + last_name + "','" + gender + "','" + email + "','" + password + "')")
        conn.commit()
        flash("Account has been created!")
        return redirect(url_for('home'))
    return render_template('createUser.html', form=create_user_form)


@app.route('/patientLogin', methods=['GET', 'POST'])
def userLogin():
    patient_login_form = patientLogin(request.form)
    if request.method == 'POST' and patient_login_form.validate():
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        email = request.form['email']
        print(email)
        query = "SELECT * FROM patients where email='" + email + "' "
        c.execute(query)
        results = c.fetchall()
        print(results)


        return render_template('patientHome.html', data=results)
    return render_template('patientLogin.html', form=patient_login_form)


@app.route('/employeeLogin', methods=['GET', 'POST'])
def employeeLogin():
    employee_login_form = EmployeeLogin(request.form)
    if request.method == 'POST' and employee_login_form.validate():
        email = request.form['email']
        conn = sqlite3.connect('employee.db')
        c = conn.cursor()
        query = "SELECT * FROM doctor where doc_email_address='" + email + "' "
        c.execute(query)
        results = c.fetchall()
        print(results)
        if len(results) != 0:
            return redirect(url_for("retrieve_customers"))
        else:
            return render_template('index.html')

    return render_template('employeeLogin.html', form=employee_login_form)


@app.route('/patientHome')
def patientHome():
    return render_template('patientHome.html')


@app.route('/deletePage/<int:id>', methods=['GET', 'POST'])
def deleteUser(id):
    patient_login_form = patientLogin(request.form)
    if request.method == 'POST' and patient_login_form.validate():
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        email = request.form['email']
        print(email)
        delete = "DELETE from patients WHERE email='" + email + "' "
        c.execute(delete)
        conn.commit()
        c.close()
        flash("Account deleted!")
        return redirect(url_for('home'))
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    query = "SELECT * FROM patients where id= '" + str(id) + "' "
    c.execute(query)
    results = c.fetchall()
    print(results)
    return render_template('deletePage.html', form=patient_login_form , data=results)


@app.route('/updatePage/<int:id>', methods=['GET', 'POST'])
def updatePage(id):
    update_user_form = UpdateUserForm(request.form)
    if request.method == 'POST' and update_user_form.validate():
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        email = request.form['email']
        print(email)
        query = "SELECT * FROM patients where email='" + email + "' "
        c.execute(query)
        results = c.fetchall()
        print(results)
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        print(first_name, last_name)
        print(results[0])

        c.execute("UPDATE patients SET first_name = '" + first_name + " 'WHERE email = '" + email + "'")
        conn.commit()

        c.execute("UPDATE patients SET last_name = '" + last_name + "' WHERE email = '" + email + "'")
        conn.commit()
        c.close()
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        query = "SELECT * FROM patients where id= '" + str(id) + "' "
        c.execute(query)
        results = c.fetchall()
        print(results)
        flash("Account has been updated!")
        return render_template('patientHome.html', data=results)
    else:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        query = "SELECT * FROM patients where id= '" + str(id) + "' "
        c.execute(query)
        results = c.fetchall()
        print(results)
        return render_template('updatePage.html', form=update_user_form , data=results)

@app.route('/OtpPage', methods=['GET', 'POST'])
def otpPage():
    forgot_password_form = OtpForm(request.form)
    if request.method == 'POST' and forgot_password_form.validate():
        otp = random.randint(1111,9999)
        email = request.form['email']
        msg = Message('PR Care OTP', sender='prcaremanagement@outlook.com', recipients=[email])
        msg.body = f"Do no show this to anybody! This is the OTP: {otp}"
        mail.send(msg)
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        query = "SELECT id FROM patients where email='" + email + "' "
        c.execute(query)
        results = c.fetchall()
        if len(results) != 0:
            c.execute("UPDATE patients SET password = '" + str(otp) + "' WHERE email = '" + email + "'")
            conn.commit()
            results = results[0][0]
            flash("OTP has been sent to your email!")

            return redirect(url_for('forgotPassPage', id=results))

        else:
            conn = sqlite3.connect('employee.db')
            c = conn.cursor()
            c.execute("UPDATE doctor SET doc_password = '" + str(otp) + "' WHERE doc_email_address = '" + email + "'")
            conn.commit()
            query = "SELECT doc_id FROM doctor where email='" + email + "' "
            c.execute(query)
            results = c.fetchall()
            results = results[0][0]
            flash("OTP has been sent to your email!")
            return redirect(url_for('forgotPassPage', id=results))



    return render_template('otp.html', form=forgot_password_form )


@app.route('/forgotPassPage/<int:id>', methods=['GET', 'POST'])
def forgotPassPage(id):
    forgot_password_form = ForgotPasswordForm(request.form)
    if request.method == 'POST' and forgot_password_form.validate():
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        query = "SELECT * FROM patients where id='" + str(id) + "' "
        c.execute(query)
        results = c.fetchall()
        if len(results) != 0:
            otp = request.form['otp']
            password = request.form['password']
            query = "SELECT password FROM patients where id='" + str(id) + "' "
            c.execute(query)
            results = c.fetchall()
            if results[0][0] == str(otp):
                c.execute("UPDATE patients SET password = '" + password + "' WHERE id = '" + str(id) + "'")
                conn.commit()
                flash("Password Changed!")
                return redirect(url_for('home'))
            else:
                flash('Incorrect OTP! Please try again!')
                return render_template('forgotPassPage.html',form=forgot_password_form)

        else:
            c.close()
            conn = sqlite3.connect('employee.db')
            c = conn.cursor()
            otp = request.form['otp']
            password = request.form['password']
            query = "SELECT doc_password FROM doctor where doc_id='" + str(id) + "' "
            c.execute(query)
            results = c.fetchall()
            if results[0][0] == str(otp):
                c.execute("UPDATE doctor SET doc_password = '" + password + "' WHERE doc_id = '" + str(id) + "'")
                conn.commit()
                flash("Password Changed!")
                return redirect(url_for('home'))
            else:
                flash('Incorrect OTP! Please try again!')
                return render_template('forgotPassPage.html',form=forgot_password_form)

    return render_template('forgotPassPage.html', form=forgot_password_form)


@app.route('/createBooking/<int:id>', methods=['GET', 'POST'])
def create_booking(id):
    create_user_form = CreateBooking(request.form)
    if request.method == 'POST' and create_user_form.validate():
        print('here')
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        query = "SELECT first_name,last_name ,email FROM patients where id= '" + str(id) + "' "
        c.execute(query)
        results = c.fetchall()
        print(results)
        first_name = results[0][0]
        last_name = results[0][1]
        email = results[0][2]
        timeslot = request.form['timeslot']
        test_remarks = request.form['remarks']
        remarks = test_remarks.lower()
        date = request.form['date']
        availability = "pending"
        doctor = "pending"
        conn = sqlite3.connect('database.db')
        print(first_name + last_name + email + date + timeslot + remarks + availability + doctor)
        c = conn.cursor()
        c.execute(
            "INSERT INTO bookings (first_name,last_name,email,date,timeslot,remarks,availability,doctor) VALUES ('" + first_name + "','" + last_name + "','" + email + "','" + date + "','" + timeslot + "','" + remarks + "','" + availability + "','" + doctor + "')")
        conn.commit()
        c.close()
        return redirect(url_for('retrieve_patient_booking', id=id))
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    query = "SELECT * FROM patients where id= '" + str(id) + "' "
    c.execute(query)
    results = c.fetchall()
    print(results)
    return render_template('createBooking.html', form=create_user_form , data=results)


@app.route('/retrievePatientsBooking/<int:id>')
def retrieve_patient_booking(id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    try:
        id = str(id)
        query = "SELECT email FROM patients WHERE id = '" + id + "'"
        c.execute(query)
        results = c.fetchall()
        print(results)
        email = results[0][0]

        query = "SELECT * FROM bookings where email = '" + email + "'"
        c.execute(query)
        results = c.fetchall()
        new_results = list(results)
    except:
        return render_template('error.html')
    query = "SELECT * FROM patients where id= '" + str(id) + "' "
    c.execute(query)
    results = c.fetchall()
    print(results)

    return render_template('retrieveUsers.html', results=new_results, data=results)


@app.route('/retrieveCustomers')
def retrieve_customers():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    query = "SELECT * FROM bookings"
    c.execute(query)
    results = c.fetchall()
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    query = "SELECT * FROM bookings"
    c.execute(query)
    count = c.fetchmany()
    new_results = list(results)
    return render_template('retrieveCustomers.html', results=new_results, count=count)


@app.route('/updateUser/<int:id>/<int:pid>', methods=['GET', 'POST'])
def update_user(id,pid):
    update_user_form = CreateBooking(request.form)
    if request.method == 'POST':
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        test_remarks = request.form['remarks']
        remarks = test_remarks.lower()
        c.execute("UPDATE bookings SET remarks = '" + remarks + "' WHERE id = '" + str(id) + "'")
        conn.commit()
        query = "SELECT * FROM bookings where id='" + str(id) + "'"
        c.execute(query)
        results = c.fetchall()
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        query = "SELECT * FROM patients where id= '" + str(pid) + "' "
        c.execute(query)
        result = c.fetchall()
        print(results)
        return render_template('retrieveUsers.html', id=pid , data=result , results=results)
    else:

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        query = "SELECT * FROM patients where id= '" + str(pid) + "' "
        c.execute(query)
        results = c.fetchall()
        print(results)
        return render_template('updateBooking.html', form=update_user_form, data=results)


@app.route('/updateCustomer/<int:id>/', methods=['GET', 'POST'])
def update_customer(id):
    update_user_form = CreateBooking(request.form)
    if request.method == 'POST':
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        availability = request.form['availability']
        test_doctor = request.form['doctor']
        doctor = test_doctor.lower()
        c.execute("UPDATE bookings SET availability = '" + availability + "' WHERE id = '" + str(id) + "'")
        c.execute("UPDATE bookings SET doctor = '" + doctor + "' WHERE id = '" + str(id) + "'")
        conn.commit()
        query = "SELECT email FROM bookings where id='" + str(id) + "'"
        c.execute(query)
        email = c.fetchall()
        email = email[0][0]
        msg = Message('PR Care OTP', sender='prcaremanagement@outlook.com', recipients=[email])
        msg.body = f"Hi this email is send to you to tell you that your booking is {availability} and your doctor is {doctor}.  "
        mail.send(msg)
        query = "SELECT * FROM bookings where id='" + str(id) + "'"
        c.execute(query)
        results = c.fetchall()
        return render_template('retrieveCustomers.html', results=results)
    else:
        return render_template('updateCustomer.html', form=update_user_form)


@app.route('/deleteUser/<int:id>/<int:pid>', methods=['POST'])
def delete_user(id,pid):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    delete = "DELETE from bookings WHERE id='" + str(id) + "' "
    c.execute(delete)
    conn.commit()
    c.close()

    return redirect(url_for('retrieve_patient_booking',id=pid))

@app.route('/deleteUsers/<int:id>', methods=['POST'])
def delete_users(id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    delete = "DELETE from bookings WHERE id='" + str(id) + "' "
    c.execute(delete)
    conn.commit()
    c.close()

    return redirect(url_for('retrieve_customer'))



@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/ERROR')
def error():
    return render_template('error.html')


if __name__ == '__main__':
    app.run()
