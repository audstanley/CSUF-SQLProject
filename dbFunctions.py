import sqlite3
import pushover
from sqlite3 import Error

"""
  Make a credentials.pushover file.  This will not be pushed to github, because
  *.pushover is ignored in the .gitignore file.  DON'T push your credientials to
  github.  The credential file will look like this inside:

  [pushover]
  # fill in the values with your app token and user key
  # save this file as .pushover in your project directory.
  # go to https://pushover.net/apps/build to create an app key
  app_key = ###############################
  # put your user key from http://pushover.net here 
  user_key = ##############################

"""
linkToApprove = 'http://localhost:5000/approveUser/'
client = pushover.PushoverClient("./credentials.pushover")

print('\n\nDatabase Operations:')

"""

  #-------------------------------------------
  #  USERS.DB FUNCTIONS
  #-------------------------------------------

"""

def initPending(initEmail, initHashword, hashLink):
  print('    ' + initEmail.lower() + '\n      ' + initHashword + '\n      ' + hashLink)
  conn = sqlite3.connect('users.db', check_same_thread=False)
  c = conn.cursor()
  """
  :param arg1: The users email address.
  :param arg2: A bcrypt password, hashed and salted.
  :param arg3: A random hash to be pushed to cell phone for approval.
  :return: True if user was successfully added to database
  :rtype Bool
  .. note: This function creates a pending user in the pendingUsers.db
      Once the user is approved with an API link that is generated
      with a random hash, the pending_user will be moved over to the
        user table.  The user table will be the table that is checked 
        on login.
  .. todo: test to see if this works
  """
  try:
    args = [initEmail.lower(), initHashword, str(hashLink)]
    c.execute('''CREATE TABLE IF NOT EXISTS pending_users
             (email string PRIMARY KEY, 
             hashword string NOT NULL,
             hashlink string NOT NULL)''')
    c.execute('INSERT INTO pending_users (email, hashword, hashlink) VALUES (?, ?, ?)', args)
    conn.commit()
    client.send_message('User ' + initEmail + ' has just registered. Click ' + linkToApprove + hashLink + ' \
      to approve the new user.')
    return True
  except Error as e:
    print(e)
    return False

def checkPendingUser(email):
  """
    docstring
  """
  conn = sqlite3.connect('users.db', check_same_thread=False)
  c = conn.cursor()
  try:
    c.execute('''SELECT email,hashword,hashlink FROM pending_users WHERE email == "%s"''' % email.lower())
    userPending = c.fetchall()
    if len(userPending) > 0:
      print(userPending)
      c.execute('''SELECT email,hashword,hashlink FROM users WHERE email == "%s"''' % email.lower())
      user = c.fetchall()
      if len(user) > 0:
        return False
      return False
    else:
      return True
      print('There is no pending user with the email address:', email)
  except Error as e:
    print(e)

def initUser(hashLink):
  """
    :param arg1: A hash that was generated for a pending_user. Not the password hash.
    :return: a dict with either an email key value, or an error
    :rtype: dict

    .. note:  This hash will be pushed to the admins as a link, example:
      http://ww2.audstanley.com:5000/usersPending/awdoOOIdwahwaoawhdODHawOHADWhwiwad292822baiiawidu
      where "awdoOOIdwahwaoawhdODHawOHADWhwiwad292822baiiawidu" would be the hashlink.
      Flask will approve that user once an admin clicks on the link.
      We will use the pushover API and the pushover android app to make the link push our cell phones.

    .. todo: test to see if this function works.

  """
  conn = sqlite3.connect('users.db', check_same_thread=False)
  c = conn.cursor()
  
  try:
    c.execute('''SELECT email,hashword FROM pending_users WHERE hashlink ="%s"''' % hashLink)
    email, hashPass = c.fetchone()
    #if len(vals) > 0:
      #email = vals[0][0]
      #hashPass = vals[0][1]
    if email is not None and hashPass is not None:
      print('initPending',email,hashPass)
      print('pending user:', email, ' was found, moving them to the user table.')
      c.execute('''CREATE TABLE IF NOT EXISTS users
              (email string PRIMARY KEY, 
              hashword string NOT NULL)''')
      c.execute('INSERT INTO users (email, hashword) VALUES (?, ?)', (email, hashPass))
      conn.commit()
      makeTables(email)
      # Begin generate Fake Students for new user
      populateTables(email, 123, 456, 'Richard', 'Stanley')
      populateTables(email, 234, 567, 'Georden', 'Grabuskie')
      populateTables(email, 345, 678, 'Chantelle', 'Bril')
      # End fake student generator
      
      return { 'email': email }
    else:
      return { 'error': 'That has hashlink does not match any email in the pending_users table' }
  except Error as e:
    print(e)
    return { 'error': str(e) }

def getHashwordFromEmail(email):
  conn = sqlite3.connect('users.db', check_same_thread=False)
  c = conn.cursor()
  try:
    c.execute('''SELECT hashword FROM users WHERE email ="%s"''' % email)
    hashword = c.fetchone()
    #print('HASHWORD:', hashword[0].encode('utf-8'))
    if hashword is not None:
      if len(hashword) > 0:
        return hashword[0].encode('utf-8')
    return None
  except Error as e:
    print('Some issue in requesting email ', e)
    return None


"""

  #-------------------------------------------
  #  *EMAIL_ADDRESS*.DB FUNCTIONS
  #-------------------------------------------

"""

def makeTables(email):
  conn = sqlite3.connect('./userDatabases/' + email + '.db', check_same_thread=False)
  c = conn.cursor()
  print("  Creating tables:")
  """
    This function creates all the tables we need.
    It's important to wrap every sql query in a try/except
    block since pyton will crash if there is an error.
      For example:
        if the table students already exists, 
        then c.execute->CREATE TABLE STUDENTS will throw an exception.
  """
  try:
    c.execute('''CREATE TABLE IF NOT EXISTS students
             (ssn integer PRIMARY KEY, 
             studentId integer NOT NULL, 
             fname text NOT NULL, 
             lname text NOT NULL)''')
    conn.commit()
  except Error as e:
    print(e)

def populateTables(email, ssn, sId, fname, lname):
  conn = sqlite3.connect('./userDatabases/' + email + '.db', check_same_thread=False)
  c = conn.cursor()
  print "  Populating student table:", ssn, sId, fname, lname
  try:
    c.execute('''INSERT INTO students
             (ssn, studentId, fname, lname)
             values(?,?,?,?)''', (ssn, sId, fname, lname))

    conn.commit()
  except Error as e:
    print(e)
  pass

def getStudentTable(email):
  conn = sqlite3.connect('./userDatabases/' + email + '.db', check_same_thread=False)
  c = conn.cursor()
  try:
    c.execute('''SELECT * FROM students''')
    return c.fetchall()
  except Error as e:
    print(e)

def deleteAllTables(email):
  conn = sqlite3.connect('./userDatabases/' + email + '.db', check_same_thread=False)
  c = conn.cursor()
  print("  Deleting tables:")
  try:
    c.execute('''DROP TABLE students''')
    conn.commit()
  except Error as e:
    print(e)
  pass  
