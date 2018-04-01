import sqlite3
from sqlite3 import Error
from flask import Flask, render_template, redirect, request

conn = sqlite3.connect('project.db')
c = conn.cursor()
app = Flask(__name__)

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
  print("  Populating tables:")
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

# This is so we start with a fresh database on every restart.
deleteAllTables()
makeTables()
populateTables(123, 456, 'Richard', 'Stanley')
populateTables(234, 567, 'Georden', 'Grabuskie')
populateTables(345, 678, 'Chantelle', 'Bril')
print(getStudentTable())

# Here is the Flask API.  We should look into the 
# flask documentation for render_template
@app.route("/")
def index():
  return render_template('homepage.html', someDataHere='yo yo yo')


if __name__ == '__main__':
  try:
    app.run(port=5000, debug=True)
  except KeyboardInterrupt:
    print("Keyboard interupt, Closing database.")
    conn.close()
