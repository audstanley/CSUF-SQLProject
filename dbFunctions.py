import sqlite3
from sqlite3 import Error

print('\n\nDatabase Operations:')

"""

  #-------------------------------------------
  #  USERS.DB FUNCTIONS
  #-------------------------------------------

"""



def initPending(initEmail, initHashword, hashLink):
  print('    ' + initEmail + '\n      ' + initHashword + '\n      ' + hashLink)
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
    args = [initEmail, initHashword, hashLink]
    c.execute('''CREATE TABLE IF NOT EXISTS pending_users
             (email string PRIMARY KEY, 
             hashword string NOT NULL,
             hashlink string NOT NULL)''')
    c.execute('INSERT INTO pending_users (email, hashword, hashlink) VALUES (?, ?, ?)', args)
    conn.commit()
    return True
  except Error as e:
    print(e)
    return False


def checkPendingUser(email, hashWord):
  """
    docstring
  """
  conn = sqlite3.connect('users.db', check_same_thread=False)
  c = conn.cursor()
  try:
    c.execute('''SELECT email,hashword FROM pending_users WHERE email == "%s"''' % email)
    user = c.fetchall()
    if len(user) > 0:
      print(user)
    else:
      print('There is no pending user with the email address:', email)
  except Error as e:
    print(e)

def initUser(hashLink):
  """
    :param arg1: A hash that was generated for a pending_user. Not the password hash.
    :return: Void
    :rtype: Void

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
    email, hashPass = c.execute('''SELECT email,password FROM pending_users WHERE hashlink == "%s"''' % hashLink)
    if email is not None and hashPass is not None:
      print('pending user:', email, ' was found, moving them to the user table.')
      c.execute('''CREATE TABLE IF NOT EXISTS users
              (email string PRIMARY KEY, 
              hashword string NOT NULL)''')
      c.execute('INSERT INTO users (email, hashword) VALUES (?, ?)', email, hashPass)
      conn.commit()
  except Error as e:
    print(e)





"""

  #-------------------------------------------
  #  *EMAIL_ADDRESS*.DB FUNCTIONS
  #-------------------------------------------

"""

def makeTables(email):
  conn = sqlite3.connect(email + '.db', check_same_thread=False)
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
  conn = sqlite3.connect(email + '.db', check_same_thread=False)
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
  conn = sqlite3.connect(email + '.db', check_same_thread=False)
  c = conn.cursor()
  try:
    c.execute('''SELECT * FROM students''')
    return c.fetchall()
  except Error as e:
    print(e)

def deleteAllTables(email):
  conn = sqlite3.connect(email + '.db', check_same_thread=False)
  c = conn.cursor()
  print("  Deleting tables:")
  try:
    c.execute('''DROP TABLE students''')
    conn.commit()
  except Error as e:
    print(e)
  pass  
