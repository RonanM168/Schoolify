#!/usr/local/bin/python3

from cgitb import enable
enable()

from cgi import FieldStorage, escape
import pymysql as db
from hashlib import sha256
from datetime import date
from shelve import open
from http.cookies import SimpleCookie
from os import environ
from html import escape


no_student_JSAlert=''
result = ''
today=date.today()
today_string = str(today)
parent_id = ''

# PERSONAL IFNO
student_firstname = ''
student_lastname = ''
parent_firstname = ''
parent_lastname = ''
contact_number=''
teacher_name=' '
form_data = FieldStorage()
student_id = ''
address = ''
eircode = ''
personal_info = ''
date_of_birth = ''
# HOMEWORK
homework_table =""
# POINTS
class_points_table = ''
student_specific_points = ''
points_reason = ''
points_date = ''
points_chart = ''
points = 0
points_string = ''
student_specific_points_graph = ''
student_specific_points_graph_script = ''
# SCHEDULE
current_class = ''
events_table = ''
event_date = ''
event_description = ''
event_date_input = ''
event_descrition_input = ''
event_id = ''
'default'
attendance_table=''
attendance_taken=False
x=''
child_id_1=''
child_id_2=''
child_1_details=''
child_2_details=''
all_children_attendance_table=''

student_id_to_name_dict={}
attendance_list=[]
class_ids_list=[]
daily_attendance_dict=dict()
student_specific_attendance_dict={'2020-02-05':'no student selected', '2020-02-06':'no student selected', '2020-02-07':'no student selected'}
#daily_attendance_dict=student_specific_attendance_dict
simple=''
presence_dict=dict()

cookie = SimpleCookie()
http_cookie_header = environ.get('HTTP_COOKIE')

#if cookie present
if http_cookie_header:
    cookie.load(http_cookie_header)
    #if sid cookie
    if 'sid' in cookie:
        sid = cookie['sid'].value
        session_store = open('sess_' + sid, writeback=False)
        #if authenticated cookie redirect to homepage
        if session_store['authenticated']:
            if session_store['account_type'] == "1":
                try:
                    teacher_name=session_store['name']
                    current_class = session_store['class']
                    parent_id = session_store['id']

                    connection = db.connect('cs1.ucc.ie', 'rjf1', 'ahf1Aeho', '2021_rjf1')
                    # PERSONAL INFO

                    # Fetching data from database tables
                    cursor = connection.cursor(db.cursors.DictCursor)
                    cursor.execute("""SELECT * FROM students where student_id in (SELECT student_id FROM student_parent WHERE parent_id=%s)"""% parent_id)

                    for row in cursor.fetchall():
                        student_id = str(row['student_id'])
                        student_firstname = row['first_name']
                        student_lastname = row['last_name']

                        cursor2 = connection.cursor(db.cursors.DictCursor)
                        cursor2.execute("""SELECT * FROM parents where child1=%s or child2=%s or child3=%s or child4=%s"""% (student_id,student_id,student_id,student_id))
                        for row2 in cursor2.fetchall():
                            parent_firstname = row2['first_name']
                            parent_lastname = row2['last_name']
                        cursor2.close()

                        cursor3 = connection.cursor(db.cursors.DictCursor)
                        cursor3.execute("""SELECT * FROM addresses WHERE student_id=%s"""% student_id)
                        for row3 in cursor3.fetchall():
                            address = row3['address']
                            eircode = row3['eircode']
                        cursor3.close()

                        # Creating table for students personal information
                        date_of_birth = str(row['date_of_birth'])
                        contact_number = str(row['phone_number'])
                        personal_info += "<tr>"
                        personal_info += "<td>" + student_firstname + " " + student_lastname + "</td>"
                        personal_info += "<td>" + parent_firstname + " " + parent_lastname +"</td>"
                        personal_info += "<td>" + date_of_birth + "</td>"
                        personal_info += "<td>" + address + "</td>"
                        personal_info += "<td>" + eircode + "</td>"
                        personal_info += "<td>" + contact_number + "</td>"
                        events_table += "</tr>"
                    connection.commit()
                    cursor.close()

                    # ATTENDANCE

                     # get the childrens id's
                    cursor = connection.cursor(db.cursors.DictCursor)
                    cursor.execute("""SELECT * FROM parents
                                            WHERE id = %s""" % (parent_id))
                    fetched = cursor.fetchone()
                    child_id_1=fetched['child1']
                    child_id_2=fetched['child2']
                    cursor.close()

                    cursor = connection.cursor(db.cursors.DictCursor)
                    cursor.execute("""SELECT * FROM students
                                            WHERE student_id=%s or student_id=%s""" % (child_id_1, child_id_2))

                    fetched=cursor.fetchall()
                    place_list=[]
                    id_list=[]
                    cursor.close()

                    # iterate for each of the parent's children
                    for child in fetched:
                        cursor = connection.cursor(db.cursors.DictCursor)
                        cursor.execute("""SELECT * FROM classes
                                                WHERE id=%s""" % (child['class']))

                        temp_counter=0
                        child_index=0
                        for id in (cursor.fetchone()['student_ids']).split():
                            if id==str(child['student_id']):
                                child_index=temp_counter
                            else:
                                temp_counter += 1
                        cursor.close()

                        student_specific_attendance_table='''
                            <h2> %s's Attendance </h2>
                          <table class="table table-striped">
                            <thead class="thead-dark">
                              <tr>
                                <th scope="col">Date</th>
                                <th scope="col">Attendance</th>
                              </tr>
                            </thead>
                            <tbody>''' % (child['first_name'])
                        cursor = connection.cursor(db.cursors.DictCursor)
                        cursor.execute("""SELECT * FROM attendance
                                                WHERE class=%s and date between '2020-02-05' and '2020-02-07'""" % (child['class']))
                        for row in cursor.fetchall():
                            if list(row['attendance'])[child_index]=='1':
                                attendance_val='Present'
                            elif list(row['attendance'])[child_index]=='0':
                                attendance_val='Absent'
                            else:
                                student_specific_attendance_dict[row['date']]='N/A'

                            student_specific_attendance_table+='''<tbody>
                              <tr>
                                <td>%s</td>
                                <td>%s</td>
                              </tr>
                            ''' % (row['date'], attendance_val)
                        cursor.close()
                        student_specific_attendance_table+='''</tbody>
                                                        </table>'''

                        all_children_attendance_table+=student_specific_attendance_table


                    cursor = connection.cursor(db.cursors.DictCursor)
                    cursor.execute("""SELECT * FROM students
                                            WHERE class = '1'""")
                    for row in cursor.fetchall():
                        student_id_to_name_dict[str(row['student_id'])]=row['first_name'] + " " + row['last_name']

                    cursor.close()

                    # CLASS ID'S
                    cursor = connection.cursor(db.cursors.DictCursor)
                    cursor.execute("""SELECT student_ids FROM classes
                                WHERE id=1""")

                    class_ids_list=cursor.fetchone()['student_ids'].split()
                    cursor.close()


                    # CLASS ATTENDANCE
                    cursor = connection.cursor(db.cursors.DictCursor)
                    cursor.execute("""SELECT attendance FROM attendance
                                WHERE class=1 and date='2020-02-14'""")
                    fetched=cursor.fetchone()
                    if(fetched==None):

                        cursor.close()
                        cursor = connection.cursor(db.cursors.DictCursor)
                        cursor.execute("""INSERT INTO attendance
                                    VALUES('2020-02-14', 1, '222')""")
                        connection.commit()
                        cursor.close()

                    else:

                        attendance_list= list(fetched['attendance'])
                        for i in range(0, len(attendance_list)):
                            if attendance_list[i]=='0':
                                attendance_taken=True
                                daily_attendance_dict[student_id_to_name_dict[class_ids_list[i]]]='Absent'
                            elif attendance_list[i]=='1':
                                attendance_taken=True
                                daily_attendance_dict[student_id_to_name_dict[class_ids_list[i]]]='Present'
                            elif attendance_list[i]=='2':
                                daily_attendance_dict[student_id_to_name_dict[class_ids_list[i]]]='Attendance Not Taken'

                    cursor.close()

                    # POINTS
                    # Retrieving the total points of the parents children and creating a table
                    cursor = connection.cursor(db.cursors.DictCursor)
                    cursor.execute("""SELECT * FROM points_total WHERE student_id in (SELECT student_id from student_parent WHERE parent_id=%s)""" % (parent_id))
                    result = current_class
                    for row in cursor.fetchall():
                        student_id = str(row['student_id'])
                        cursor2 = connection.cursor(db.cursors.DictCursor)
                        cursor2.execute("""SELECT * FROM students WHERE student_id=%s""" % (student_id))
                        for row2 in cursor2.fetchall():
                            student_firstname = row2['first_name']
                            student_lastname = row2['last_name']
                        connection.commit()
                        cursor2.close()
                        total_points = str(row['points'])
                        class_points_table += "<tr>"
                        class_points_table += "<td>" + student_firstname + " " + student_lastname + "</td>"
                        class_points_table += "<td>" + total_points + "</td>"
                        class_points_table += "</tr>"
                        # Adding the students total points to the bar chart
                        points_chart +="{ y: " + total_points +", label: \"" + student_firstname + " " + student_lastname + "\" },"
                    connection.commit()
                    cursor.close()

                    # STUDENT_SPECIFIC POINTS

                    # Creating a table for each child showing their specific points and reasons
                    cursor = connection.cursor(db.cursors.DictCursor)
                    cursor.execute("""SELECT * FROM students where student_id in (SELECT student_id FROM student_parent WHERE parent_id=%s)"""% parent_id)

                    for row in cursor.fetchall():
                        points = 0
                        student_firstname = row['first_name']
                        student_id = str(row['student_id'])
                        student_specific_points += """<div id="student-specific-points"class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pb-2 mb-3 border-bottom">
                                                        <h1 class="h2">""" + student_firstname + """\'s Points</h1>
                                                    </div>"""
                        student_specific_points += """<table class="table table-hover reasons-table">
                                                      <thead class="thead-dark">
                                                        <tr>
                                                          <th class="date" scope="col">Date</th>
                                                          <th class="event" scope="col">Reason</th>
                                                        </tr>
                                                      </thead>
                                                      <tbody>"""
                        # Creating a graph for each student showing their points history
                        student_specific_points_graph_script += """var chart""" + student_id + """ = new CanvasJS.Chart(\"chartContainer""" + student_id + """\", {
                                                                        animationEnabled: true,
                                                                        theme: "light2",
                                                                        title:{
                                                                            text: \"""" + student_firstname + """ \'s Points History\"
                                                                        },
                                                                        axisY:{
                                                                            title: "Total Points",
                                                                            includeZero: false
                                                                        },
                                                                        data: [{
                                                                        		type: "line",
                                                                              	indexLabelFontSize: 16,
                                                                        		dataPoints: [{ y: 0, label: \" \", }, """
                        # Inserting data into individual students tables
                        cursor2 = connection.cursor(db.cursors.DictCursor)
                        cursor2.execute("""SELECT * FROM points_reasons WHERE student_id = %s ORDER BY reason_date""" % (student_id))
                        for row2 in cursor2.fetchall():
                            points_date = str(row2['reason_date'])
                            points_reason = row2['reason']
                            points += int(row2['points'])
                            points_string = str(points)
                            student_specific_points += "<tr>"
                            student_specific_points += "<td>" + points_date + "</td>"
                            student_specific_points += "<td>" + points_reason + "</td>"
                            student_specific_points += "</tr>"
                            # Inserting data into script for points graphs
                            student_specific_points_graph_script += "{ y: " + points_string +", label: \"" + points_date + " \", },"

                        student_specific_points += """</tbody>
                                                    </table>"""
                        student_specific_points_graph_script += """
                                                                            ]
                                                                    }]
                                                                });
                                                                chart""" + student_id + """.render();"""

                        student_specific_points_graph += "<div id=\"chartContainer" + student_id + "\" class=\"chartContainer\"></div>"
                        # HOMEWORK
                        teacher_email = ''
                        cursor4 = connection.cursor(db.cursors.DictCursor)
                        cursor4.execute("""SELECT email FROM teachers
                                        WHERE class =
                                        (SELECT class FROM students
                                        WHERE student_id = '%s');""" % (student_id))
                        for row in cursor4.fetchall():
                            teacher_email = row['email']
                        cursor4.close()
                        homework_table += """
                                            <div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pb-2 mb-3 border-bottom">
                                                    <h1 class="h2">%s's Tests</h1>
                                            </div>
                                            <table>
    						                     <tr>
    							                   <th>Week</th>
    							                   <th>Submission</th>
                                                   <th>Result</th>
                                                   <th>Comments</th>
    						                     </tr>""" % (student_firstname)
                        cursor3 = connection.cursor(db.cursors.DictCursor)
                            # currently using a workaround where instead of sending the eamil of teacher_name
                            # from login.py I'm using the teacher_name@gamil.com
                        cursor3.execute("""SELECT * FROM homework
                                        WHERE student_id = '%s'
                                        AND teacher_email = '%s'""" % (student_id, teacher_email))

                        week =1
                            # append all file submissions even if null
                        for row in cursor3.fetchall():
                            # Currently all files are in correct order so no need to use file_order atribute yet
                            # as this simplifies matters a lot
                            # Changed the file structure for where homework files will be stored to make it easier
                            homework_table += """<tr>
                                                    <td>Week %s</td>
                                                    <td><a href="tests/%s/%s" download>Solution</a></td>
                                                    <td> %s </td>
                                                    <td> %s </td>
                                                </tr>""" % (str(week),student_id, row['filename'], str(row['result']), row['comments'])
                            week+=1
                        homework_table += """</table>
                                            <p></p>"""
                        cursor3.close()

                    cursor.close()


                    # SCHEDULE

                    # Delete events that have already happened
                    cursor = connection.cursor(db.cursors.DictCursor)
                    cursor.execute("""SELECT * FROM calendar WHERE class = %s ORDER BY event_date""" % (current_class))
                    for row in cursor.fetchall():
                        event_date = str(row['event_date'])
                        if event_date < today_string:
                            cursor2 = connection.cursor(db.cursors.DictCursor)
                            cursor2.execute("""DELETE FROM calendar WHERE event_date='%s'""" % (event_date))
                            cursor2.close()
                    cursor.close()

                    # Create events table
                    cursor = connection.cursor(db.cursors.DictCursor)
                    cursor.execute("""SELECT * FROM calendar WHERE class = %s ORDER BY event_date""" % (current_class))

                    for row in cursor.fetchall():
                        event_date = str(row['event_date'])
                        event_description = row['event_description']
                        event_id = str(row['id'])
                        events_table += "<tr>"
                        events_table += "<td>" + event_date + "</td>"
                        events_table += "<td>" + event_description + "</td>"
                        events_table += "</tr>"
                    connection.commit()
                    cursor.close()

                    student_firstname = ''
                    student_lastname = ''
                    student_id = ''

                    # Discussion

                    printer = ""
                    counter = 0
                    teacher_id = session_store['id']
                    cursor = connection.cursor(db.cursors.DictCursor)

                    cursor.execute("""SELECT * FROM discussion_board WHERE sender_id = %s""" % (teacher_id))

                    for row in cursor.fetchall():
                        counter += 1
                        sender_id = row['sender_id']
                        receiver_id = row["receiver_id"]
                        cursor2 = connection.cursor(db.cursors.DictCursor)
                        cursor2.execute("SELECT * FROM parents WHERE id = %s" % (receiver_id))

                        for row in cursor2.fetchall():
                            parent_firstname = row["first_name"]
                        cursor2.close()
                        printer += "<tr>"
                        printer += "<td>"
                        printer += parent_firstname
                        printer += "</td>"
                        printer += "<td>"
                        printer += "<button class='discussion_buttons' onclick='displayDiscussion(%s)'>Click to open</button>" % (counter)
                        printer += "</td>"
                        printer += "</tr>"
                        printer += "<p hidden id=sender_id+%s>%s</p>" % (counter, sender_id)
                        printer += "<p hidden id=receiver_id+%s>%s</p>" % (counter, receiver_id)
                    connection.commit()
                    cursor.close()
                    connection.close()


                except db.Error:
                    result = '<p>Sorry! We are experiencing problems at the moment. Please call back later.</p>'

                if len(form_data) != 0:

                    try:
                        # check which input fields contain data
                        # and from with source, i.e. from searching or from adding event
                        try:
                            student_id = escape(form_data.getfirst('student_id'))
                        except:
                            student_id = ''
                        try:
                            student_1_attendance = escape(form_data.getfirst('optradio1'))
                        except:
                            student_1_attendance = '2'
                        try:
                            student_2_attendance = escape(form_data.getfirst('optradio2'))
                        except:
                            student_2_attendance = '2'
                        try:
                            student_3_attendance = escape(form_data.getfirst('optradio3'))
                        except:
                            student_3_attendance = '2'
                        try:
                            file_upload = escape(form_data.getfirst('filename'))
                        except:
                            file_upload = ''


                        # UPDATE ATTENDANCE

                        connection = db.connect('cs1.ucc.ie', 'rjf1', 'ahf1Aeho', '2021_rjf1')

                        cursor = connection.cursor(db.cursors.DictCursor)
                        cursor.execute("""UPDATE attendance
                                    SET attendance=%s WHERE date='2020-02-14'""" % (student_1_attendance+student_2_attendance+student_3_attendance))
                        connection.commit()
                        cursor.close()

                        if student_id != '':

                            # PERSONAL INFO

                            # Creating personal info table for specified student
                            personal_info = ''
                            cursor = connection.cursor(db.cursors.DictCursor)
                            cursor.execute("""SELECT * FROM students
                                            WHERE student_id = %s and student_id IN (SELECT student_id FROM student_parent WHERE parent_id=%s)""" % (student_id, parent_id))
                            fetched = cursor.fetchall()
                            if len(fetched)==0:
                                no_student_JSAlert='alert("This Isn\'t Your Child\'s Student ID. Search for a Valid Student ID.");'
                            else:
                                for row in fetched:
                                    student_id = str(row['student_id'])
                                    student_firstname = row['first_name']
                                    student_lastname = row['last_name']

                                    cursor2 = connection.cursor(db.cursors.DictCursor)
                                    cursor2.execute("""SELECT * FROM parents where child1=%s or child2=%s or child3=%s or child4=%s"""% (student_id,student_id,student_id,student_id))
                                    for row2 in cursor2.fetchall():
                                        parent_firstname = row2['first_name']
                                        parent_lastname = row2['last_name']
                                    cursor2.close()

                                    cursor3 = connection.cursor(db.cursors.DictCursor)
                                    cursor3.execute("""SELECT * FROM addresses WHERE student_id=%s"""% student_id)
                                    for row3 in cursor3.fetchall():
                                        address = row3['address']
                                        eircode = row3['eircode']
                                    cursor3.close()

                                    date_of_birth = str(row['date_of_birth'])
                                    contact_number = str(row['phone_number'])
                                    personal_info += "<tr>"
                                    personal_info += "<td>" + student_firstname + " " + student_lastname + "</td>"
                                    personal_info += "<td>" + parent_firstname + " " + parent_lastname +"</td>"
                                    personal_info += "<td>" + date_of_birth + "</td>"
                                    personal_info += "<td>" + address + "</td>"
                                    personal_info += "<td>" + eircode + "</td>"
                                    personal_info += "<td>" + contact_number + "</td>"
                                    events_table += "</tr>"
                                connection.commit()
                            cursor.close()


                            # STUDENT-SPECIFIC ATTENDANCE
                            student_index=0
                            for i in range(len(class_ids_list)):

                                if class_ids_list[i]==str(student_id):
                                    student_index=i
                            x=student_index
                            cursor = connection.cursor(db.cursors.DictCursor)

                            cursor.execute("""SELECT * FROM attendance
                                            WHERE class=1 and date between '2020-02-05' and '2020-02-07'""")

                            # clear the dictionary for new entries
                            student_specific_attendance_dict.clear()
                            for row in cursor.fetchall():
                                if list(row['attendance'])[student_index]=='1':
                                    student_specific_attendance_dict[row['date']]='Present'
                                elif list(row['attendance'])[student_index]=='0':
                                    student_specific_attendance_dict[row['date']]='Absent'
                                else:
                                    student_specific_attendance_dict[row['date']]='N/A'


                            cursor.close()

                        connection.close()


                    except db.Error:
                        result = '<p>Sorry! We are experiencing problems at the moment. Please call back later.</p>'
            else:
                print('Location:login.py')
        else:
            print('Location: login.py')
    else:
        print('Location: login.py')
else:
    print('Location: login.py')
if not attendance_taken:
    attendance_table=attendance_table="""<h1>Take Daily Attendance</h1>
    <form action="parent.py" onsubmit="post();return false;">
    <table class="table table-hover">
      <thead class="thead-dark">
        <tr>
          <th scope="col">#</th>
          <th scope="col">Student Name</th>
          <th scope="col">Present</th>
          <th scope="col">Absent</th>
        </tr>
      </thead>
      <tbody>

        <tr>
          <th scope="row">1</th>
          <td>%s</td>
          <td><input type="radio" name="optradio1" value="1"></td>
          <td><input type="radio" name="optradio1" value="0"></td>
        </tr>
        <tr>
          <th scope="row">2</th>
          <td>%s</td>
          <td><input type="radio" name="optradio2" value="1"></td>
          <td><input type="radio" name="optradio2" value="0"></td>
        </tr>
        <tr>
          <th scope="row">3</th>
          <td>%s</td>
          <td><input type="radio" name="optradio3" value="1"></td>
          <td><input type="radio" name="optradio3" value="0"></td>
        </tr>

        </tbody>
      </table>
      <input type="submit" value="Submit" />


      </form>""" % (student_id_to_name_dict[class_ids_list[0]],\
      student_id_to_name_dict[class_ids_list[1]],\
      student_id_to_name_dict[class_ids_list[2]])

print('Content-Type: text/html')
print()

print("""
    <!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">


        <!-- Bootstrap CSS -->
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css" integrity="sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh" crossorigin="anonymous">
        <!-- Overriding CSS -->
        <link rel="stylesheet" href="./css/style.css">
        <link rel="icon" href="./assets/favicon.ico" type="image/x-icon">
        <link href='fullcalendar/core/main.css' rel='stylesheet' />
        <link href='fullcalendar/daygrid/main.css' rel='stylesheet' />

        <!-- FontAwesome Icons -->
        <script src="https://kit.fontawesome.com/44c51e0d9c.js" crossorigin="anonymous"></script>
        <!-- Script to ensure dashboard is loaded on launch -->
        <script type="text/javascript">
            if (document.location.hash == "" || document.location.hash == "#")
                document.location.hash = "#dashboard";
        </script>

        <script src='fullcalendar/core/main.js'></script>
        <script src='fullcalendar/daygrid/main.js'></script>
        <script src="canvasjs.min.js"></script>

        <script>

          document.addEventListener('DOMContentLoaded', function() {
            var calendarEl = document.getElementById('calendar');

            var calendar = new FullCalendar.Calendar(calendarEl, {
              plugins: [ 'dayGrid' ]
            });

            calendar.render();
          });

        </script>

        <script>
        window.onload = function () {

        var chart1 = new CanvasJS.Chart("chartContainer1", {
        	animationEnabled: true,
        	theme: "light2", // "light1", "light2", "dark1", "dark2"
        	title:{
        		text: "Student Points"
        	},
        	axisY: {
        		title: "Total Points"
        	},
        	data: [{
        		type: "column",
        		dataPoints: [
        			%s
        		]
        	}]
        });
        chart1.render();

        %s

        }
        </script>


        <title>Schoolify</title>
      </head>
      <body>

        <script>
            function myFunction() {
                %s
            }
            myFunction()
        </script>

        <script>
            function displayDiscussion(checker) {
                get_sender = 'sender_id+' + checker
                get_receiver = 'receiver_id+' + checker
                var sender_id = document.getElementById(get_sender).innerHTML;
                var receiver_id = document.getElementById(get_receiver).innerHTML;
                xmlhttp = new XMLHttpRequest();
                xmlhttp.onreadystatechange = function() {
                    if (this.readyState == 4 && this.status == 200) {
                        document.getElementById("current_discussion").innerHTML = this.responseText;
                    }
                };
                xmlhttp.open("GET","get_discussion.php?q="+sender_id+"&k="+receiver_id,true);
                xmlhttp.send();
            }
        </script>

        <!--<div class="current-student-container container"></div>-->

        <div class="view-options container-fluid">
          <div class="row">

            <nav class="sidebar col-md-2 d-none d-md-block">

              <ul class="nav flex-column">
                <li>
                  <img src="./assets/just_logo_whiteBG.png" width="60px" height="60px">
                  <a class="#nav-link" href="parent.py">Schoolify</a>
                </li>

                <!--Search Form-->
                <li class="search_bar">
                    <form class="form-inline d-flex justify-content-center md-form form-sm mt-0" action="parent.py" method="get">
                        <i class="fas fa-search" aria-hidden="true"></i>
                        <input class="form-control form-control-sm ml-3 w-75" name="student_id" value="%s" type="text" placeholder="Student ID" aria-label="Search">
                    </form>
                </li>
                <li>
                  <!--<div class="row col-md-2" id="top-row">Student</div>               -->
                  Student: <strong>%s %s</strong>
                </li>
                <li>
                  <i class="fas fa-user-graduate"></i>
                  <a class="#nav-link" href="#personal-info">Personal Information</a>
                </li>
                <li>
                  <i class="fas fa-clock"></i>
                  <a class="#nav-link" href="#attendance">Attendance</a>
                </li>
                <li>
                  <i class="fas fa-chart-bar"></i>
                  <a class="#nav-link" href="#points">Points</a>
                </li>
                <li>
                  <i class="fas fa-edit"></i>
                  <a class="#nav-link" href="#tests">Tests</a>
                </li>
                <li>
                  <i class="far fa-calendar"></i>
                  <a class="#nav-link" href="#schedule">Schedule</a>
                </li>
                <li>
                    <i class="far fa-comment-dots"></i>
                    <a class="#nav-link" href="#discussion">Discussion Board</a>
                </li>
                <li class="logout-button">
                  <i class="fas fa-sign-out-alt"></i>
                  <a class="#nav-link" href="./logout.py">Logout</a>
                </li>
              </ul>
              </nav>
              <main role="main" class="col-md-9 ml-sm-auto col-lg-10 pt-3 px-4">

                  <!--Below are the hidden content sections for the student-->
                  <div class="hidden-content">
                    <div id="dashboard">
                          <div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pb-2 mb-3 border-bottom">
                              <h1 class="h2">Dashboard<p id="date">%s</p></h1>

                              <div class="align-items-end profile-header-container">
    		                    <div class="profile-header-img">
                                    <img class="img-circle" src="./assets/parent/rachel.jpg" />
                                </div>
                               </div>
                          </div>
                          <p>Welcome back %s</p>
                          <h1>Today's Attendance</h1>
                          <table class="table table-hover">
                            <thead class="thead-dark">
                              <tr>
                                <th scope="col">#</th>
                                <th scope="col">Student Name</th>
                                <th scope="col">Attendance</th>
                              </tr>
                            </thead>
                            <tbody>
                              <tr>
                                <th scope="row">1</th>
                                <td>Peter Ahern</td>
                                <td>Present</td>
                              </tr>
                              <tr>
                                <th scope="row">2</th>
                                <td>Aoife Ahern</td>
                                <td>Present</td>
                              </tr>
                             </tbody>
                            </table>

                    </div>

                    <!-- PERSONAL INFO -->
                    <div class="col-md-8" id="personal-info">
                        <div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pb-2 mb-3 border-bottom">
                            <h1 class="h2">Personal Information</h1>
                        </div>
                        <table class="table table-hover personal-info-table">
                          <thead class="thead-dark">
                            <tr>
                              <th class="date" scope="col">Student</th>
                              <th class="event" scope="col">Parent</th>
                              <th class="event" scope="col">DOB</th>
                              <th class="event" scope="col">Address</th>
                              <th class="event" scope="col">Eircode</th>
                              <th class="event" scope="col">Contact Number</th>
                            </tr>
                          </thead>
                          <tbody>
                            %s
                        </tbody>
                        </table>
                    </div>

                    <!-- Children's Attendace -->
                    <div id="attendance">
                        <div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pb-2 mb-3 border-bottom">
                            <h1 class="h2">Attendance for Your Children</h1>
                        </div>
                    %s

                    </div>


                    <div id="points">
                        <div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pb-2 mb-3 border-bottom">
                            <h1 class="h2">Class Points</h1>
                        </div>
                        <table class="table table-hover points-table">
                          <thead class="thead-dark">
                            <tr>
                              <th class="student-name" scope="col">Student Name</th>
                              <th class="student-points" scope="col">Points Accumulated</th>
                            </tr>
                          </thead>
                          <tbody>
                            %s
                          </tbody>
                        </table>
                        %s
                        <div id="chartContainer1"></div>
                        %s
                    </div>

                    <div id="tests">
    					<div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pb-2 mb-3 border-bottom">
                            <h1 class="h2">Tests</h1>
                        </div>
    						<!-- creating these table rows dynamically now so that more rows can be added when needed-->
                        %s
                    </div>

                    <div id="schedule">
                        <div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pb-2 mb-3 border-bottom">
                            <h1 class="h2">Schedule</h1>
                        </div>
                        <div id='calendar'></div>

                        <div id="events-schedule">
                            <table class="table table-hover events-table">
                              <thead class="thead-dark">
                                <tr>
                                  <th class="date" scope="col">Date</th>
                                  <th class="event" scope="col">Event</th>
                                </tr>
                              </thead>
                              <tbody>
                                %s
                            </tbody>
                            </table>
                        </div>

                    </div>
                    <div id="discussion">
                        <div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pb-2 mb-3 border-bottom">
                            <h1 class="h2">Discussion Board</h1>
                        </div>
                        <div id="conversations">
                            <table>
                                <thead class="thead-dark">
                                    <tr>
                                        <th class="active_conversations" scope="col">Active Conversations</th>
                                        <th class="visit_conversation" scope="col">Visit Conversation</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    %s
                                </tbody>
                            </table>
                            <div>
                                <p id="current_discussion"></p>
                            </div>
                        </div>
                    </div>
                </div>
              </main>
            </div>
          </div>

        <script src="https://code.jquery.com/jquery-3.4.1.slim.min.js" integrity="sha384-J6qa4849blE2+poT4WnyKhv5vZF5SrPo0iEjwBvKU7imGFAV0wwj1yYfoRSJoZ+n" crossorigin="anonymous"></script>
        <script src="https://cdn.jsdelivr.net/npm/popper.js@1.16.0/dist/umd/popper.min.js" integrity="sha384-Q6E9RHvbIyZFJoft+2mJbHaEWldlvI9IOYy5n3zV9zzTtmI3UksdQRVvoxMfooAo" crossorigin="anonymous"></script>
        <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/js/bootstrap.min.js" integrity="sha384-wfSDF2E50Y2D1uUdj0O3uMBJnjuUD4Ih7YwaYd1iqfktj0Uod8GCExl3Og8ifwB6" crossorigin="anonymous"></script>
      </body>
    </html>
    """ % (points_chart, student_specific_points_graph_script,\
     no_student_JSAlert, student_id, student_firstname, student_lastname,\
    today, teacher_name,\
      personal_info, \
      all_children_attendance_table, \
      class_points_table, student_specific_points, student_specific_points_graph, homework_table,\
       events_table, printer))
