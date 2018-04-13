from flask import Flask, render_template, redirect, request, session, url_for
from dbFunctionsClass import db
from flask_login import LoginManager
from flask_wtf import FlaskForm
from base64 import b64encode, b64decode
import random
import string
from wtforms import Form, StringField, PasswordField, validators
from os import urandom #salt
import bcrypt

db = db()

def randHashlink():
  return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in range(32))

print('  Example of hashLink:\n    ' +  randHashlink())

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

class sqlQueryForm(FlaskForm):
  query = StringField('query', [validators.DataRequired()])

# see https://flask-login.readthedocs.io/en/latest/#installation
# for the flask-login module documentation

# This is so we start with a fresh database on every restart.
db.deleteAllTables('audstanley@gmail.com')
db.makeTables('audstanley@gmail.com')
db.populateTables('audstanley@gmail.com', 1234, 'Richard', 'Stanley',   '123 Stanley St.', 'Lake Forest', 'CA', 92630, 9499030246)
db.populateTables('audstanley@gmail.com', 2345, 'Georden', 'Grabuskie', '123 Stanley St.', 'Lake Forest', 'CA', 92630, 9499030246)
db.populateTables('audstanley@gmail.com', 3456, 'Chantelle', 'Bril',    '123 Stanley St.', 'Lake Forest', 'CA', 92630, 9499030246)


# Generate fake pending users:
print('  Generating fake pending users:')
db.initPending('newUser@yahoo.com', bcrypt.hashpw('password', bcrypt.gensalt()), randHashlink())
db.initPending('newUser@hotmail.com', bcrypt.hashpw('password', bcrypt.gensalt()), randHashlink())
db.initPending('newUser@gmail.com', bcrypt.hashpw('password', bcrypt.gensalt()), randHashlink())
db.initPending('newUser@netflix.com', bcrypt.hashpw('password', bcrypt.gensalt()), randHashlink())
# Generate fake users:
print('  Generating fake users:')


# Here is the Flask API.  We should look into the 
# flask documentation for render_template
@app.route("/")
def index():
  if 'logged_in' in session:
    if session['logged_in'] == True:
      print(session)
      studentTable = db.getStudentTable('audstanley@gmail.com')
      studentTableMap = map(lambda x: dict({'sId': str(x[0]), 'fname': x[1], 'lname': x[2], 
        'street': x[3], 'city': x[4], 'state': x[5], 'zip': str(x[6]), 
        'phone': str(x[7])[0:3] + '-' + str(x[7])[3:6] + '-' + str(x[7])[6:10] }), studentTable)
      #return redirect('login')
      return render_template('homepage.html', studentTableMap=studentTableMap)
    else:
      return redirect('login')
  else:
    return redirect('login')


@app.route('/login', methods=['GET', 'POST'])
def login():
  form = LoginForm()
  
  #sqlForm = sqlQueryForm()
  if form.validate_on_submit():
    hashword = db.getHashwordFromEmail(request.form['username'].lower())
    #print('BCRYPT:', bcrypt.checkpw(request.form['password'].encode('utf-8'), hashword))
    if hashword is not None:
      if bcrypt.checkpw(request.form['password'].encode('utf-8'), hashword):
        emailAddress = request.form['username'].lower().encode('utf-8')
        session['username'] = emailAddress
        session['logged_in'] = True
        db.setCookie(str(emailAddress), str(session['csrf_token']))
        return redirect('home/' + session['csrf_token'])
      else:
        return 'Incorrect password'
    else:
      return 'Unsuccessful Login'
    
    #c.execute('IF EXISTS (SELECT hashword FROM pending_students WHERE email = ?)', request.form["username"])
    #if bcrypt.checkpw(password, hashword):
    #  print("Password verified.")
  else:
    print("Incorrect username or password!")
    print(form.data)
    return render_template('login.html', login=form)

@app.route('/logout/<cookie>')
def logout(cookie):
   # remove the username from the session if it is there
   db.emptyCookie(cookie)
   return redirect(url_for('login'))

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

          # Make sure the user doesn't already exists:
          if db.checkPendingUser(request.form['username']):
            db.initPending(request.form["username"], hashword, randHashlink())
            return 'Awaiting Approval from Admins'
          else:
            return 'The email ' + request.form['username'] + ' already exists. You might need to wait to \
              be approved from admins before logging in.'

          
        else:
          print("Passwords do NOT match!")
          return 'Passwords do NOT match.'
        
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

@app.route('/home/<cookie>', methods=['GET', 'POST'])
def home(cookie):
  emailAddress = db.getUserFromCookie(cookie)
  if emailAddress is not None:
    studentTable = db.getStudentTable(emailAddress)
    studentTableMap = map(lambda x: dict({'sId': str(x[0]), 'fname': x[1], 'lname': x[2], 
        'street': x[3], 'city': x[4], 'state': x[5], 'zip': str(x[6]), 'b64sId': b64encode(str(x[0])), 
        'phone': str(x[7])[0:3] + '-' + str(x[7])[3:6] + '-' + str(x[7])[6:10] }), studentTable)
    return render_template('homepage.html', studentTableMap=studentTableMap)
  else:
    return 'You have logged out.'

@app.route('/deleteStudent/<cookie>/<sId>', methods=['GET'])
def deleteStudent(cookie, sId):
  db.deleteAStudent(cookie, b64decode(sId))
  return redirect('/home/' + cookie)


@app.route('/approveUser/<hash>', methods=['GET'])
def approveUser(hash):
  #print(hash)
  newUser = db.initUser(hash)
  if newUser is not None:
    if 'email' in newUser:
      return 'New User: ' + newUser['email'] + ' has been created.'
    elif 'error' in newUser:
      return 'Error: ' + newUser['error']
  else:
    return 'User was already approved.'

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug=True)
  
