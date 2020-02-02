#!/usr/local/bin/python3

from cgitb import enable
enable()

from cgi import FieldStorage
import pymysql as db
from html import escape

print('Content-Type: text/html')
print()

result = ''
student_firstname = ''
student_lastname = ''
form_data = FieldStorage()
student_id = ''
if len(form_data) != 0:
    try:
        student_id = escape(form_data.getfirst('student_id'))
        connection = db.connect('cs1.ucc.ie', 'rjf1', 'ahf1Aeho', '2021_rjf1')
        cursor = connection.cursor(db.cursors.DictCursor)

        cursor.execute("""SELECT * FROM students
                        WHERE student_id = '%s'""" % (student_id))
        for row in cursor.fetchall():
            student_firstname = row['first_name']
            student_lastname = row['last_name']
        #result += '</table>'
        cursor.close()
        connection.close()
    except db.Error:
        result = '<p>Sorry! We are experiencing problems at the moment. Please call back later.</p>'

print("""
    <!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">


        <!-- Bootstrap CSS -->
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css" integrity="sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh" crossorigin="anonymous">
        <!-- Overriding CSS -->
        <link rel="stylesheet" href="../css/style.css">
        <link rel="icon" href="../assets/favicon.ico" type="image/x-icon">

        <!-- FontAwesome Icons -->
        <script src="https://kit.fontawesome.com/44c51e0d9c.js" crossorigin="anonymous"></script>

        <title>Schoolify</title>
      </head>
      <body>

        <!--<div class="current-student-container container"></div>-->

        <div class="view-options container-fluid">
          <div class="row">
            <nav class="sidebar col-md-2 d-none d-md-block">


              <ul class="nav flex-column">
                <li>
                  <img src="../assets/just_logo.png" width="60px" height="60px">
                  <a class="#nav-link" href="#schoolify">Schoolify</a>
                </li>
                <li>
                  <!-- Search form -->
                  <form action="teacher.py" method="get">
                      <input class="form-control" type="text" value="%s" aria-label="Search" id="student_id" />
                      <input type="submit" value="Search" />
                  </form>
                </li>
                <li>
                  <!--<div class="row col-md-2" id="top-row">Student</div>               -->
                  <strong>Student: </strong>%s %s
                </li>

                <li>
                  <i class="fas fa-user-graduate"></i>
                  <a class="#nav-link" href="#personal-info">Personal Information</a>
                </li>
                <li>
                  <i class="fas fa-copy"></i>
                  <a class="#nav-link" href="#term-reports">Term Reports</a>
                </li>
                <li>
                  <i class="fas fa-clock"></i>
                  <a class="#nav-link" href="#attendance">Attendance</a>
                </li>
                <li>
                  <i class="fas fa-edit"></i>
                  <a class="#nav-link" href="#homework">Homework</a>
                </li>
                <li>
                  <i class="far fa-calendar"></i>
                  <a class="#nav-link" href="#schedule">Schedule</a>
                </li>
              </ul>
              </nav>
            </div>
          </div>



        <!--Below are the hidden content sections for the student-->
        <div class="hidden-content">
          <div id="personal-info">
            <p>Test1</p>
          </div>
          <div id="term-reports">
            <p>Test2</p>
          </div>
          <div id="attendance">
            <p>Test3</p>
          </div>
        </div>

        <script src="https://code.jquery.com/jquery-3.4.1.slim.min.js" integrity="sha384-J6qa4849blE2+poT4WnyKhv5vZF5SrPo0iEjwBvKU7imGFAV0wwj1yYfoRSJoZ+n" crossorigin="anonymous"></script>
        <script src="https://cdn.jsdelivr.net/npm/popper.js@1.16.0/dist/umd/popper.min.js" integrity="sha384-Q6E9RHvbIyZFJoft+2mJbHaEWldlvI9IOYy5n3zV9zzTtmI3UksdQRVvoxMfooAo" crossorigin="anonymous"></script>
        <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/js/bootstrap.min.js" integrity="sha384-wfSDF2E50Y2D1uUdj0O3uMBJnjuUD4Ih7YwaYd1iqfktj0Uod8GCExl3Og8ifwB6" crossorigin="anonymous"></script>
      </body>
    </html>
    """ % (student_id, student_firstname, student_lastname))
