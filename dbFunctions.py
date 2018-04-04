import sqlite3
from sqlite3 import Error



print('\n\nDatabase Operations:')

def initPending(initEmail, initHashword):
  conn = sqlite3.connect('users.db', check_same_thread=False)
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
    args = [initEmail, initHashword]
    c.execute('''CREATE TABLE IF NOT EXISTS pending_students
             (email string PRIMARY KEY, 
             hashword string NOT NULL,
             studentID integer, 
             fname text, 
             lname text)''')
    c.execute('INSERT INTO pending_students (email, hashword) VALUES (?, ?)', args)

    conn.commit()
  except Error as e:
    print(e)


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

def get(tableName):
  pass