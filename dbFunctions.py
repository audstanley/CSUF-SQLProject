import sqlite3
from sqlite3 import Error

conn = sqlite3.connect('project.db', check_same_thread=False)
c = conn.cursor()

print('\n\nDatabase Operations:')

def makeTables():
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


def populateTables(ssn, sId, fname, lname):
  print "  Populating student table:", ssn, sId, fname, lname
  try:
    c.execute('''INSERT INTO students
             (ssn, studentId, fname, lname)
             values(?,?,?,?)''', (ssn, sId, fname, lname))

    conn.commit()
  except Error as e:
    print(e)
  pass


def getStudentTable():
  try:
    c.execute('''SELECT * FROM students''')
    return c.fetchall()
  except Error as e:
    print(e)

def deleteAllTables():
  print("  Deleting tables:")
  try:
    c.execute('''DROP TABLE students''')
    conn.commit()
  except Error as e:
    print(e)
  pass  

def get(tableName):
  pass