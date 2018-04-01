from flask import Flask, render_template, redirect, request
from dbFunctions import deleteAllTables, makeTables, populateTables, getStudentTable

app = Flask(__name__)






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
  d = getStudentTable()
  print('data:', d)
  return render_template('homepage.html', someDataHere=d)


if __name__ == '__main__':
  app.run(port=5000, debug=True)
  
