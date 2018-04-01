import sqlite3
from flask import Flask, render_template, redirect, request

conn = sqlite3.connect('project.db')
c = conn.cursor()
app = Flask(__name__)

def makeTables():
  """
    This function creates all the tables we need.
    It's important to wrap every sql query in a try/except
    block since pyton will crash if there is an error.
      For example:
        if the table students already exists, 
        then c.execute->CREATE TABLE STUDENTS will throw an exception.
  """
  try:
    c.execute('''CREATE TABLE IF EXISTS students
             (ssn, studentId, fname, lname)''')
  except:
    print('Students table already exists, no need to create.')


def deleteAllTables():
  try:
    c.execute('''DROP TABLE IF EXISTS students''')
  except:
    print('No table students exists')
  pass  


# This is so we start with a fresh database on every restart.
deleteAllTables()
makeTables()



# Here is the Flask API.  We should look into the 
# flask documentation for render_template
@app.route("/")
def index():
  return render_template('homepage.html', someDataHere='yo yo yo')



if __name__ == '__main__':
  app.run(port=5000, debug=True)
