from flask import Flask, render_template, redirect, request
from dbFunctions import deleteAllTables, makeTables, populateTables, getStudentTable, initPending
from flask_login import LoginManager
from flask_wtf import FlaskForm
from wtforms import Form, StringField, PasswordField, validators
from os import urandom #salt
import bcrypt


app = Flask(__name__)

# we will store our secrete key as a global environment variable, later
app.config['SECRET_KEY'] = 'SomeCrazyHash'

login_manager = LoginManager()
login_manager.init_app(app)

class UserForm(FlaskForm):
  email = StringField('email', [validators.DataRequired(), validators.Email()])
  password = PasswordField('password', [validators.DataRequired()])

class LoginForm(FlaskForm):
  username = StringField('email', [validators.DataRequired(), validators.Email()])
  password = PasswordField('password', [validators.DataRequired()])

class RegisterForm(FlaskForm):
  username = StringField('email', [validators.DataRequired(), validators.Email()])
  password1 = PasswordField('password', [validators.DataRequired()])
  password2 = PasswordField('password', [validators.DataRequired()])


# see https://flask-login.readthedocs.io/en/latest/#installation
# for the flask-login module documentation

# This is so we start with a fresh database on every restart.
deleteAllTables('audstanley@gmail.com')
makeTables('audstanley@gmail.com')
populateTables('audstanley@gmail.com', 123, 456, 'Richard', 'Stanley')
populateTables('audstanley@gmail.com', 234, 567, 'Georden', 'Grabuskie')
populateTables('audstanley@gmail.com', 345, 678, 'Chantelle', 'Bril')

# Here is the Flask API.  We should look into the 
# flask documentation for render_template
@app.route("/")
def index():
  d = getStudentTable('audstanley@gmail.com')

  dictData = map(lambda x: dict({'ssn':x[0], 'studentId': x[1], 'fname': x[2], 'lname': x[3]}), d)
  print 'data:', dictData
  #return redirect('login')
  return render_template('homepage.html', someDataHere=dictData)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
      c.execute('IF EXISTS (SELECT hashword FROM pending_students WHERE email = ?)', request.form["username"])
      if bcrypt.checkpw(password, hashword):
        print("Password verified.")
      else:
        print("Incorrect username or password!")
      print(form.data)
      return 'We will need to do things in the database...'
    return render_template('login.html', login=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == 'POST':
      password1 =  request.form["password1"]
      password2 =  request.form["password2"]
      if form.validate_on_submit():
        print(password1)
        print(password2)
        if (password1 == password2):
          print("Passwords match.")
          hashword = bcrypt.hashpw(password1.encode('utf-8'), bcrypt.gensalt()) #salt is prepended to hash
          # To check that an unhashed password matches one that has previously been hashed
          #if bcrypt.checkpw(password, hashed):
          #   print("It Matches!")
          #else:
          #   print("It Does not Match :(")
          initPending(request.form["username"], hashword)
        else:
          print("Passwords do NOT match!")
        
        # Need to save the CSRF token in database
        # This token will be used to access the user's personal database
        # form.data reveals the email, two passwords, and CSRF token.
        # This token changes everytime they reopen their browser,
        # so we CAN use it as a static address for their home page, as long
        # as we update the user.db everytime they LOGIN.  We might want to
        # consider saving a timestamp in the user.db for last login, so we can
        # timout the user's CSRF Token from being valid
        print(form.data)
        return 'We will need to register in the database...'
      else:
        return 'NO VALID DATA'
    return render_template('register.html', register=form)

@app.route('/home/<hash>', methods=['GET', 'POST'])
def home(hash):
  print(hash)
  return 'User Page CSRF Token: '+ hash

if __name__ == '__main__':
  app.run(port=5000, debug=True)
  
