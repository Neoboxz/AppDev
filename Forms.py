from flask import Flask, render_template,request, redirect, url_for,flash
from wtforms import *
from wtforms.fields import *
import sqlite3
import re
from datetime import *
from wtforms.validators import *


def validate_pass(form, field):
    if re.findall("[a-z]", field.data):
        if re.findall("[0-9]", field.data):
            if re.findall("[A-Z]", field.data):

                if not re.findall("[!@#$%^&*()_=+]", field.data):
                    raise ValidationError("Must have !@#$%^&*()_=+")
            else:
                raise ValidationError("Must have Capital letters!")

        else:
            raise ValidationError("Must have numbers")
    else:
        raise ValidationError("Must have letters!")


def validate_name(form, field):
    regexp = re.compile('[^a-zA-Z ]+')
    check = regexp.search(field.data)
    print(check)
    if regexp.search(field.data):
        raise ValidationError("Only Characters is Allowed")


def validate_email(form, field):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    data = field.data
    query = "SELECT email FROM patients where email='"+data+"'"
    c.execute(query)
    results = c.fetchall()
    if len(results) != 0:
        raise ValidationError("This email already exist!")

def validate_email_check(form, field):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    data = field.data
    try:
        query = "SELECT email FROM patients where email='"+data+"'"
        c.execute(query)
        results = c.fetchall()
        if len(results) == 0:
            raise ValidationError("This email doesn't exist!")
    except:
        conn = sqlite3.connect('employee.db')
        c = conn.cursor()
        query = "SELECT doc_email_address FROM doctor where doc_email_address='"+data+"'"
        c.execute(query)
        results = c.fetchall()
        if len(results) == 0:
            raise ValidationError("This email doesn't exist!")


def check(form,field):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    email = request.form['email']
    password = request.form['password']
    data = field.data
    print(email, password , data)

    query = "SELECT password FROM patients where email='"+email+"' "
    c.execute(query)
    results = c.fetchall()
    print(results)
    if len(results) != 0:
        if results[0][0] != password:
            raise ValidationError("Invalid Password or email")
    else:
        raise ValidationError("Invalid Password or email")




class CreateUserForm(Form):
    first_name = StringField('First Name', [validators.Length(min=1, max=150), validators.DataRequired(),validate_name],render_kw={"placeholder": "Andy"})
    last_name = StringField('Last Name', [validators.Length(min=1, max=150), validators.DataRequired(),validate_name],render_kw={"placeholder": "Jackson"})
    gender = SelectField('Gender', [validators.DataRequired()], choices=[ ('F', 'Female'), ('M', 'Male')],default='')
    email = EmailField('Email Address', [validators.DataRequired(),validators.Email(),validate_email],render_kw={"placeholder": "examples@examples.com"})
    password = PasswordField('Password', [validators.DataRequired(),validators.EqualTo('confirm',message='Passwords must match'),validators.Length(min=8, max=150),validate_pass],render_kw={"placeholder": "Enter password here"})
    confirm = PasswordField('Repeat Password',render_kw={"placeholder": "Type password again"})


class patientLogin(Form):
    email = EmailField('Email Address', [validators.DataRequired(),validators.Email(),],render_kw={"placeholder": "Email"})
    password = PasswordField('Password', [validators.DataRequired(),check],render_kw={"placeholder": "Password"})





class UpdateUserForm(Form):
    first_name = StringField('First Name', [validators.Length(min=1, max=150), validators.DataRequired(),validate_name],render_kw={"placeholder": "Enter your new first name"})
    last_name = StringField('Last Name', [validators.Length(min=1, max=150), validators.DataRequired(),validate_name],render_kw={"placeholder": "Enter your new last name"})
    email = EmailField('Email Address', [validators.DataRequired(),validators.Email(),validate_email_check],render_kw={"placeholder": "Enter your current email"})



class ForgotPasswordForm(Form):
    otp = StringField('Enter your OTP', [validators.DataRequired()],render_kw={"placeholder": "OTP"})
    password = PasswordField('New Password', [validators.DataRequired(),validate_pass],render_kw={"placeholder": "New Password"})
    confirm = PasswordField('Repeat New Password',render_kw={"placeholder": "Type new password again"})

class OtpForm(Form):
    email = EmailField('Email Address', [validators.DataRequired(),validators.Email(),validate_email_check],render_kw={"placeholder": "Email"})



def employee_check(form,field):
    conn = sqlite3.connect('employee.db')
    c = conn.cursor()
    email = request.form['email']
    password = request.form['password']
    data = field.data
    print(email, password , data)
    try:
        query = "SELECT password FROM users where email='"+email+"' "
        c.execute(query)
        results = c.fetchall()
        print(results)
        if len(results) != 0:
            if results[0][0] != password:
                raise ValidationError("Invalid Password or email")
        else:
            raise ValidationError("Invalid Password or email")
    except:
        doctor_query = "SELECT doc_password FROM doctor where doc_email_address='"+email+"' "
        c.execute(doctor_query)
        results = c.fetchall()
        print(results)
        if len(results) != 0:
            if results[0][0] != password:
                raise ValidationError("Invalid Password or email")
        else:
            raise ValidationError("Invalid Password or email")


class EmployeeLogin(Form):
    email = EmailField('Email Address', [validators.DataRequired(),validators.Email(),],render_kw={"placeholder": "Email"})
    password = PasswordField('Password', [validators.DataRequired(),employee_check],render_kw={"placeholder": "Password"})


doc_list = [('pending','Pending')]
conn = sqlite3.connect('employee.db')
c = conn.cursor()
query = "SELECT doc_full_name FROM doctor"
c.execute(query)
result = c.fetchall()
name1 = result[1]

for i in result:
    name1 = i[0]
    doc_tup = ('Dr '+ str(name1),'Dr '+ str(name1))
    doc_list.append(doc_tup)
print(doc_list)

def validateEmail(form,field):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    query = "SELECT * FROM patients"
    c.execute(query)
    results = c.fetchall()
    print(results)
    if field.data != results[0][3]:
        raise ValidationError('Please enter a valid email!')

def validate_date(form,field):

    today = date.today()
    min_date = today + timedelta(days=1)
    max_date = today + timedelta(days=31)

    if field.data < min_date or field.data > max_date:
        raise ValidationError(f'Please choose a date between {min_date} and {max_date}')


class CreateBooking(Form):
    email = StringField('Email', validators=[Length(min=1, max=150), DataRequired() ])
    timeslot = SelectField('Timeslot', [validators.DataRequired()], choices=[('', 'Select'), ('10am to 11am', '10am to 11am'), ('11am to 12pm', '11am to 12pm'), ('1pm to 2pm','1pm to 2pm'), ('2pm to 3pm', '2pm to 3pm'), ('3pm to 4pm', '3pm to 4pm'), ('4pm to 5pm', '4pm to 5pm')], default='')
    remarks = TextAreaField('Remarks', [validators.Optional()])
    doctor = SelectField('Doctor', [validators.Optional()],choices=doc_list)
    date = DateField('Date', validators=[DataRequired(), validate_date])
    availability = RadioField('Availability', choices=[('confirmed', 'Confirmed'), ('unavailable', 'Unavailable'), ('pending', 'Pending')], default='pending')




