from flask import Flask, render_template, redirect, request
from dbFunctions import deleteAllTables, makeTables, populateTables, getStudentTable
from flask_login import LoginManager
from flask_wtf import FlaskForm
from wtforms import Form, StringField, PasswordField, validators
from user import user

app = Flask(__name__)

# we will store our secrete key as a global environment variable, later
app.config['SECRET_KEY'] = 'SomeCrazyHash'

login_manager = LoginManager()
login_manager.init_app(app)

class UserForm(FlaskForm):
  email = StringField('email', [validators.DataRequired(), validators.Email()])
  password = PasswordField('password', [validators.DataRequired()])

class LoginForm(FlaskForm):
  username = StringField('username')
  password = PasswordField('password')


# see https://flask-login.readthedocs.io/en/latest/#installation
# for the flask-login module documentation

# This is so we start with a fresh database on every restart.
deleteAllTables()
makeTables()
populateTables(123, 456, 'Richard', 'Stanley')
populateTables(234, 567, 'Georden', 'Grabuskie')
populateTables(345, 678, 'Chantelle', 'Bril')

# Here is the Flask API.  We should look into the 
# flask documentation for render_template
@app.route("/")
def index():
  d = getStudentTable()
  dictData = map(lambda x: dict({'ssn':x[0], 'studentId': x[1], 'fname': x[2], 'lname': x[3]}), d)
  print 'data:', dictData
  return render_template('homepage.html', someDataHere=dictData)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
      return 'We will need to do things in the database...'
    return render_template('login.html', login=form)


if __name__ == '__main__':
  app.run(port=5000, debug=True)
  
