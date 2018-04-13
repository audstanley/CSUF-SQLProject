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
class db:
  def initPending(self, initEmail, initHashword, hashLink):
    """
    :param arg1: The users email address.
    :type: str
    :param arg2: A bcrypt password, hashed and salted.
    :type: str
    :param arg3: A random hash to be pushed to cell phone for approval.
    :type: str
    :return: True if user was successfully added to database
    :rtype bool
    .. note: This function creates a pending user in the pendingUsers.db
        Once the user is approved with an API link that is generated
        with a random hash, the pending_user will be moved over to the
          user table.  The user table will be the table that is checked 
          on login.
    """
    print('    ' + initEmail.lower() + '\n      ' + initHashword + '\n      ' + hashLink)
    conn = sqlite3.connect('users.db', check_same_thread=False)
    c = conn.cursor()
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

  def checkPendingUser(self, email):
    """
      :param arg1: email
      :type: str
      :return: Whether or not there is a user pending to be approved
      :rtype: bool
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

  def initUser(self, hashLink):
    """
      :param arg1: A hash that was generated for a pending_user. Not the password hash.
      :type: str
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
                hashword string NOT NULL,
                cookie string NOT NULL)''')
        c.execute('INSERT INTO users (email, hashword, cookie) VALUES (?, ?, ?)', (email, hashPass, ''))
        conn.commit()
        self.makeTables(email)
        # Begin generate Fake Students for new user
        self.populateTables(email, 1234, 'Richard', 'Stanley',   '123 Stanley St.', 'Lake Forest', 'CA', 92630, 9499030246)
        self.populateTables(email, 2345, 'Georden', 'Grabuskie', '123 Stanley St.', 'Lake Forest', 'CA', 92630, 9499030246)
        self.populateTables(email, 3456, 'Chantelle', 'Bril',    '123 Stanley St.', 'Lake Forest', 'CA', 92630, 9499030246)
        # End fake student generator
        
        return { 'email': email }
      else:
        return { 'error': 'That has hashlink does not match any email in the pending_users table' }
    except Error as e:
      print(e)
      return { 'error': str(e) }

  def setCookie(self, email, cookie):
    """
      :param arg1: email address of the user
      :type: str
      :param arg2: The cookie to set in the users table
      :type: str
      :return: void
      :rtype: void
    """
    conn = sqlite3.connect('users.db', check_same_thread=False)
    c = conn.cursor()
    print("SET COOKIE EMAIL: " + email + " COOKIE: " + cookie)
    try:
      c.execute('''UPDATE users SET cookie = ? WHERE users.email = ?''' , (cookie, email))
      conn.commit()
    except Error as e:
      print('could not update cookie for: ' + email + ' Error: ' + str(e))

  def getUserFromCookie(self, cookie):
    """
      :param arg1: cookie that the user is using in their browser
      :type: str
      :return: their email address
      :rtype: str, or None (if cookie does not exists in db)
    """
    conn = sqlite3.connect('users.db', check_same_thread=False)
    c = conn.cursor()
    try:
      c.execute('''SELECT email FROM users WHERE cookie = "%s"''' % cookie)
      result = c.fetchone()
      conn.commit()
      if result > 0:
        return str(result[0])
      else:
        return None
    except Error as e:
      print('getUserFromCookie function Error: ' + str(e))

  def emptyCookie(self, cookie):
    """
      :param arg1: cookie that the user is using in their browser
      :type: str
      :return: void
      :rtype: void
    """
    conn = sqlite3.connect('users.db', check_same_thread=False)
    c = conn.cursor()
    try:
      c.execute('''UPDATE users SET cookie = ? WHERE users.cookie = ?''', ('', cookie))
      conn.commit()
    except Error as e:
      print('EMPTY COOKIE ERROR: ' + str(e))

  def getHashwordFromEmail(self, email):
    """
      :param arg1: email
      :type: str
      :return: hasword, which is a hash of the user's password
      :rtype: str, or None (if the email is not in the db)
    """
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

  def makeTables(self, email):
    """
      :param arg1: email
      :type: str
      :return: void
      :rtype: void
    """
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
              (studentId integer PRIMARY KEY, 
              fname text NOT NULL, 
              lname text NOT NULL,
              street text NOT NULL,
              city text NOT NULL,
              state text NOT NULL,
              zip integer NOT NULL,
              phone text NOT NULL
              )''')
      conn.commit()
    except Error as e:
      print(e)

  def populateTables(self,email,sId,fname,lname,st,city,state,zipCode,phone):
    """
      :param arg1: email
      :type: str
      :param arg2: student Id
      :type: int
      :param arg3: first name
      :type: str
      :param arg4: last name
      :type: str
      :param arg5: street
      :type: str
      :param arg6: city
      :type: str
      :param arg7: state
      :type: str
      :param arg8: zip code
      :type: int
      :param arg9: phones
      :type: str
      :return: void
      :rtype: void
    """
    conn = sqlite3.connect('./userDatabases/' + email + '.db', check_same_thread=False)
    c = conn.cursor()
    print "  Populating student table:",sId,fname,lname,st,city,state,zipCode,phone
    try:
      c.execute('''INSERT INTO students
              (studentId,fname,lname,street,city,state,zip,phone)
              values(?,?,?,?,?,?,?,?)''', (sId,fname,lname,st,city,state,zipCode,phone))

      conn.commit()
    except Error as e:
      print(e)
    pass

  def getStudentTable(self, email):
    """
      :param arg1: email
      :type: str
      :return: void
      :rtype: void
    """
    conn = sqlite3.connect('./userDatabases/' + email + '.db', check_same_thread=False)
    c = conn.cursor()
    try:
      c.execute('''SELECT * FROM students''')
      return c.fetchall()
    except Error as e:
      print(e)

  def deleteAStudent(self, cookie, sId):
    """
      :param arg1: cookie
      :type: str
      :param arg2: student Id
      :type: str
      :return: void
      :rtype: void
    """
    email = self.getUserFromCookie(cookie)
    if email is not None:
      try:
        conn = sqlite3.connect('./userDatabases/' + email + '.db', check_same_thread=False)
        c = conn.cursor()
        c.execute('''DELETE FROM students WHERE studentId = "%s"''' % sId)
        conn.commit()
      except Error as e:
        print(str(e))

  def deleteAllTables(self, email):
    """
      :param arg1: email
      :type: str
      :return: void
      :rtype: void
    """
    conn = sqlite3.connect('./userDatabases/' + email + '.db', check_same_thread=False)
    c = conn.cursor()
    print("  Deleting tables:")
    try:
      c.execute('''DROP TABLE students''')
      conn.commit()
    except Error as e:
      print(e)
    pass  
